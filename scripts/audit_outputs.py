#!/usr/bin/env python3
"""Read-only checks for rendered slide PNGs and native PPTX objects; not visual QA."""
import argparse
import io
import json
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

NS = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
}
RID = '{' + NS['r'] + '}id'


def relationships(z, part):
    rel_path = posixpath.join(posixpath.dirname(part), '_rels', posixpath.basename(part) + '.rels')
    if rel_path not in z.namelist():
        return {}
    result = {}
    for rel in ET.fromstring(z.read(rel_path)):
        target = rel.attrib.get('Target', '')
        external = rel.attrib.get('TargetMode') == 'External'
        resolved = target if external else (
            target.lstrip('/') if target.startswith('/') else
            posixpath.normpath(posixpath.join(posixpath.dirname(part), target)))
        result[rel.attrib['Id']] = {'target': resolved, 'external': external,
                                    'type': rel.attrib.get('Type', '')}
    return result


def audit_images(folder, expected, report):
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError('Image inspection needs Pillow in the chosen Python runtime.') from exc
    if not folder.is_dir():
        report['issues'].append(f'Image directory does not exist: {folder}')
        return
    files = sorted(p for p in folder.iterdir() if re.fullmatch(r'S\d{2,}\.png', p.name))
    if not files:
        report['issues'].append('No final images named S01.png, S02.png, ... were found.')
    if expected is not None and len(files) != expected:
        report['issues'].append(f'Image count {len(files)} != expected {expected}.')
    records = []
    for index, path in enumerate(files, 1):
        if path.stem != f'S{index:02d}':
            report['issues'].append(f'Image numbering gap at {path.name}.')
        with Image.open(path) as im:
            im.load()
            w, h = im.size
            if abs(w * 9 - h * 16) > 16:  # at most one output pixel rounding
                report['issues'].append(f'{path.name}: {w}x{h} is not 16:9.')
            if w < 1600 or h < 900:
                report['warnings'].append(f'{path.name}: low resolution {w}x{h}; inspect projected readability.')
            records.append({'file': str(path), 'width': w, 'height': h})
    report['images'] = records


def audit_pptx(path, plan_slides, expected, report):
    with ZipFile(path) as z:
        corrupt = z.testzip()
        if corrupt:
            raise ValueError(f'Corrupt ZIP member: {corrupt}')
        pres = ET.fromstring(z.read('ppt/presentation.xml'))
        size = pres.find('p:sldSz', NS)
        if size is None:
            raise ValueError('PPTX lacks an explicit slide size.')
        w, h = int(size.attrib['cx']), int(size.attrib['cy'])
        if abs(w * 9 - h * 16) > 16:
            report['issues'].append('PPTX canvas is not 16:9.')
        rels = relationships(z, 'ppt/presentation.xml')
        ids = pres.findall('p:sldIdLst/p:sldId', NS)
        if expected is not None and len(ids) != expected:
            report['issues'].append(f'PPTX count {len(ids)} != expected {expected}.')
        if not ids:
            report['issues'].append('PPTX contains no slides.')
        records = []
        for index, sid in enumerate(ids, 1):
            part = rels[sid.attrib[RID]]['target']
            root = ET.fromstring(z.read(part))
            text_shapes = [s for s in root.findall('.//p:sp', NS)
                           if any((t.text or '').strip() for t in s.findall('.//a:t', NS))]
            names = [n.attrib.get('name', '') for n in root.findall('.//p:cNvPr', NS)]
            counts = {
                'text': len(text_shapes),
                'table': len(root.findall('.//a:tbl', NS)),
                'chart': len(root.findall('.//c:chart', NS)),
                'diagram_nodes': sum(n.startswith('diagram-') for n in names),
                'formula': len(root.findall('.//m:oMath', NS)),
                'pictures': len(root.findall('.//p:pic', NS)),
                'connectors': len(root.findall('.//p:cxnSp', NS)),
            }
            label = f'S{index:02d}'
            if counts['text'] == 0:
                report['issues'].append(f'{label}: no nonempty native text shapes; inspect raster-only content.')
            expected_objects = plan_slides[index - 1].get('expected_objects', {}) if index <= len(plan_slides) else {}
            for kind, minimum in expected_objects.items():
                if kind in counts and counts[kind] < minimum:
                    report['issues'].append(f'{label}: native {kind}={counts[kind]}, expected at least {minimum}.')
            large_pictures = []
            for pic in root.findall('.//p:pic', NS):
                xf = pic.find('p:spPr/a:xfrm', NS)
                if xf is None:
                    continue
                off, ext = xf.find('a:off', NS), xf.find('a:ext', NS)
                if off is None or ext is None:
                    continue
                x, y = int(off.attrib['x']), int(off.attrib['y'])
                pw, ph = int(ext.attrib['cx']), int(ext.attrib['cy'])
                clipped_area = max(0, min(w, x + pw) - max(0, x)) * max(0, min(h, y + ph) - max(0, y))
                coverage = clipped_area / (w * h)
                if coverage >= 0.85:
                    nv = pic.find('p:nvPicPr/p:cNvPr', NS)
                    large_pictures.append({'name': nv.attrib.get('name', '') if nv is not None else '',
                                           'coverage': round(coverage, 3)})
            if large_pictures:
                report['warnings'].append(f'{label}: image covers >=85% of canvas; verify it is only decoration, not flattened slide content.')
            if root.findall('.//p:grpSp', NS):
                report['warnings'].append(f'{label}: grouped shapes present; picture coverage ignores group coordinate transforms.')
            slide_rels = relationships(z, part)
            chart_data = []
            for chart in root.findall('.//c:chart', NS):
                chart_rel = slide_rels.get(chart.attrib.get(RID, ''))
                if not chart_rel or chart_rel['external'] or chart_rel['target'] not in z.namelist():
                    report['issues'].append(f'{label}: missing or external native chart part.')
                    continue
                chart_path = chart_rel['target']
                chart_root = ET.fromstring(z.read(chart_path))
                ext_data = chart_root.find('.//c:externalData', NS)
                data_rel = relationships(z, chart_path).get(ext_data.attrib.get(RID, '')) if ext_data is not None else None
                has_workbook = bool(data_rel and not data_rel['external'] and
                                    data_rel['type'].endswith('/package') and data_rel['target'] in z.namelist())
                if has_workbook:
                    try:
                        with ZipFile(io.BytesIO(z.read(data_rel['target']))) as workbook:
                            members = workbook.namelist()
                            has_workbook = (workbook.testzip() is None and
                                            'xl/workbook.xml' in members and '[Content_Types].xml' in members and
                                            any(re.fullmatch(r'xl/worksheets/sheet\d+\.xml', n) for n in members))
                    except Exception:
                        has_workbook = False
                chart_data.append({'part': chart_path, 'embedded_data': has_workbook})
                if not has_workbook:
                    report['warnings'].append(f'{label}: chart {chart_path} has no verified embedded data workbook; confirm data editing.')
            records.append({'id': label, 'part': part, 'counts': counts,
                            'large_pictures': large_pictures, 'chart_data': chart_data})
        report['pptx'] = {'path': str(path), 'canvas_emu': [w, h], 'slides': records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--renders', '--images', dest='images', type=Path,
                        help='Final PPT render directory; --images is a compatibility alias.')
    parser.add_argument('--pptx', type=Path)
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    if not args.images and not args.pptx:
        parser.error('Provide --renders, --pptx, or both.')
    report = {'issues': [], 'warnings': [],
              'scope': 'Static checks only; overlaps, connector direction/endpoints, visual match, factual accuracy, visibility, and interactive editability need review.'}
    expected, slides = None, []
    try:
        if args.plan:
            plan = json.loads(args.plan.read_text(encoding='utf-8'))
            slides = plan['slides']
            expected = plan['slide_count']
            if not isinstance(expected, int) or isinstance(expected, bool) or expected <= 0:
                raise ValueError('slide_count must be a positive integer.')
            if len(slides) != expected:
                report['issues'].append('Content plan slides length differs from slide_count.')
            for i, slide in enumerate(slides, 1):
                if slide.get('id') != f'S{i:02d}':
                    report['issues'].append(f'Content plan has nonsequential id at slide {i}.')
                allowed = {'text', 'table', 'chart', 'diagram_nodes', 'formula'}
                if set(slide.get('expected_objects', {})) - allowed:
                    raise ValueError('Unknown expected_objects type; use text, table, chart, diagram_nodes, or formula.')
                for minimum in slide.get('expected_objects', {}).values():
                    if not isinstance(minimum, int) or isinstance(minimum, bool) or minimum < 0:
                        raise ValueError('expected_objects counts must be nonnegative integers.')
        if args.images:
            audit_images(args.images, expected, report)
        if args.pptx:
            audit_pptx(args.pptx, slides, expected, report)
    except Exception as exc:
        report['issues'].append(f'{type(exc).__name__}: {exc}')
    report['static_status'] = 'issues_found' if report['issues'] else 'passed_static_checks'
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report['issues'] else 0


if __name__ == '__main__':
    sys.exit(main())
