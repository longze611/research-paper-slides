# Research Paper Slides

用于 Codex 的科研论文汇报技能，仿照顶会论文报告的 PPT 风格，适合文献汇报、组会和学术报告。

输入是一篇论文，生成效果如这份完整的 [12 页英文示例 PPT](examples/smart-contract-fuzzers.pptx) 所示。示例输入为 Wu et al. 的论文 [Are We There Yet? Unraveling the State-of-the-Art Smart Contract Fuzzers](https://arxiv.org/abs/2402.02973)（ICSE 2024）。

## 安装方式

以下两种方式均安装为**当前用户全局技能**，可在不同项目中使用。请复制完整指令，不要只发送仓库链接。

### 方式一：下载 ZIP，让 Codex 安装

[下载本仓库 ZIP](https://github.com/longze611/research-paper-slides/archive/refs/heads/main.zip)，将文件提供给 Codex，并发送：

```text
请将这个 ZIP 中的 research-paper-slides 安装为当前用户的全局 Codex 技能。
默认安装到 ~/.agents/skills/research-paper-slides/；若当前客户端明确使用旧版技能目录，
则使用 $CODEX_HOME/skills/research-paper-slides/（CODEX_HOME 未设置时为 ~/.codex/skills/research-paper-slides/）。
请实际完成安装，保留 SKILL.md、agents、references、assets、scripts 等完整资源，
确保 SKILL.md 直接位于技能目录下，不要只解压到当前项目或多嵌套一层仓库目录。
安装后检查技能名称和资源路径，并告知最终绝对路径及刷新方法；已有同名技能时先比较，保留本地修改。
```

### 方式二：复制 Git 链接，让 Codex 安装

将下面的内容发送给 Codex：

```text
请从 https://github.com/longze611/research-paper-slides.git
将仓库根目录中的 research-paper-slides 安装为当前用户的全局 Codex 技能。
默认安装到 ~/.agents/skills/research-paper-slides/；若当前客户端明确使用旧版技能目录，
则使用 $CODEX_HOME/skills/research-paper-slides/（CODEX_HOME 未设置时为 ~/.codex/skills/research-paper-slides/）。
请实际完成安装，保留完整技能资源，并确保 SKILL.md 直接位于技能目录下。
不要只克隆到当前项目；安装后检查技能名称和资源路径，告知最终绝对路径及刷新方法。
已有同名技能时先比较，保留本地修改。
```

安装后在新会话中用 `/skills` 或输入 `$research-paper-slides` 查找；未出现时重启 Codex。建议切换到另一项目再确认，以检查全局可用性。

用户级目录依据 [OpenAI 官方技能文档](https://developers.openai.com/codex/skills/)。

## 使用方式

向 Codex 提供论文 PDF，并发送：

```text
请使用 $research-paper-slides，为这篇论文制作 12 页英文汇报 PPT。
重点讲清问题、方法、关键实验和局限。
请先给我逐页结构和文案，确认后再制作。
```

可以自行指定页数、文案语言（中文或英文）和报告重点；技能会在开始时询问未明确的页数或语言，已明确的项直接沿用。

## 运行条件

- Codex 能读取论文 PDF 和本技能的参考素材。
- 当前环境提供 `Presentations` 技能，以及支持原生文本、表格、形状、连接线、PPTX 导出和逐页渲染的工具。
- PDF 阅读与图表裁切需要可用的 PDF 工具；可选静态检查脚本需要 Python 3 和 Pillow。

本仓库提供技能指令和参考素材，PPT 制作与渲染由所在 Codex 环境的工具完成。

## 交付内容

可编辑 PPTX、渲染预览及可复现的制作源文件。文字、表格和流程结构优先使用原生对象；论文原始照片、热图和缺少完整数据的曲线可保留为图片。

## 致谢与来源

风格参考及来源记录见 [参考报告研究](references/source-study.md)和[素材来源](assets/source-provenance.json)。相关报告与论文素材的权利归各自权利人所有。本技能借鉴其视觉与叙事方法，不代表原作者或会议的认可。
