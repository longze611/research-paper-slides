# Research Paper Slides

用于 Codex 的科研论文汇报技能，仿照顶会论文报告的 PPT 风格，适合文献汇报、组会和学术报告。

输入是一篇论文，生成效果如这份完整的 [12 页英文示例 PPT](examples/smart-contract-fuzzers.pptx) 所示。示例输入为 Wu et al. 的论文 [Are We There Yet? Unraveling the State-of-the-Art Smart Contract Fuzzers](https://arxiv.org/abs/2402.02973)（ICSE 2024）。

## 安装方式

### 方式一：下载 ZIP，让 Codex 安装

[下载本仓库 ZIP](https://github.com/longze611/research-paper-slides/archive/refs/heads/main.zip)，将文件提供给 Codex，并发送：

```text
请将这个 ZIP 中的 research-paper-slides 技能安装到我的 Codex 技能目录。
```

### 方式二：复制 Git 链接，让 Codex 安装

将下面的内容发送给 Codex：

```text
请从这个 Git 仓库安装 research-paper-slides 技能：
https://github.com/longze611/research-paper-slides.git
```

安装后重新打开 Codex 会话，或按当前客户端方式刷新技能列表。

## 使用方式

向 Codex 提供论文 PDF，并发送：

```text
请使用 $research-paper-slides，为这篇论文制作 12 页英文汇报 PPT。
重点讲清问题、方法、关键实验和局限。
请先给我逐页结构和文案，确认后再制作。
```

可以自行指定页数、语言和报告重点；未指定页数时，技能会先询问。

## 运行条件

- Codex 能读取论文 PDF 和本技能的参考素材。
- 当前环境提供 `Presentations` 技能，以及支持原生文本、表格、形状、连接线、PPTX 导出和逐页渲染的工具。
- PDF 阅读与图表裁切需要可用的 PDF 工具；可选静态检查脚本需要 Python 3 和 Pillow。

本仓库提供技能指令和参考素材，PPT 制作与渲染由所在 Codex 环境的工具完成。

## 交付内容

可编辑 PPTX、渲染预览及可复现的制作源文件。文字、表格和流程结构优先使用原生对象；论文原始照片、热图和缺少完整数据的曲线可保留为图片。

## 致谢与来源

风格参考及来源记录见 [参考报告研究](references/source-study.md)和[素材来源](assets/source-provenance.json)。相关报告与论文素材的权利归各自权利人所有。本技能借鉴其视觉与叙事方法，不代表原作者或会议的认可。
