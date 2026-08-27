# OpenClaw Knowledge Base Retriever 📚

<div align="center">
  <a href="README.md">🇨🇳 中文</a> | <strong>🌐 English</strong>
</div>

<p align="center">
  <img src="./assets/readme/hero.svg" width="100%" alt="OpenClaw Knowledge Base Retriever — local knowledge-base retrieval over md/pdf/xlsx: hierarchical data_structure.md index navigation + progressive search, zero dependencies">
</p>

> Local knowledge-base retrieval & QA over a local directory (md/pdf/xlsx) — hierarchical index navigation + progressive search, zero external dependencies, Windows & macOS ready.
> 本地知识库检索器——分层索引导航 + 渐进式检索，零依赖零 API key，Windows / macOS 双平台。

![license](https://img.shields.io/badge/license-MIT-green)
[![ClawHub downloads](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fclawhub.ai%2Fapi%2Fv1%2Fskills%2Fxiaoyaoclaw-kb-retriever&query=skill.stats.downloads&label=ClawHub%20downloads&color=blue)](https://clawhub.ai/dtsola/skills/xiaoyaoclaw-kb-retriever)

## Why you need it

When an OpenClaw agent faces a local knowledge base (docs / reports / data directories), common pain points:
- ❌ **Whole-file reads**: huge PDFs/Excels dumped into context, token explosion
- ❌ **Blind searching**: no index navigation, full-tree scans are slow and noisy
- ❌ **Wrong format handling**: PDF/Excel processed with the wrong tools
- ❌ **Cloud dependency**: RAG solutions need embedding models or external API keys, privacy at risk

This skill solves all of it: **hierarchical index navigation + progressive retrieval + learn-before-process + fully local, zero dependencies.**

## Features

- 🗂️ **Hierarchical index navigation**: each directory carries a `data_structure.md`; navigate the index tree instead of scanning everything
- 🔍 **Progressive retrieval**: grep/Select-String to locate → windowed reads (offset/limit) → up to 5 bounded rounds, never whole-file loads
- 📖 **Learn-before-process**: PDF/Excel handling is gated on reading the right references first
- 🐍 **Unified Python pipeline**: PDF via pdfplumber — identical behavior on Windows & macOS
- 🔒 **Fully local, zero dependencies**: no vector index, no cloud API, sensitive data never leaves your machine
- 🏗️ **One-command index build**: `python build_index.py <kb>` auto-generates the index skeleton
- 🧭 **Sourced answers**: every answer cites file + location, verifiable

## Install

```bash
# ClawHub (recommended)
clawhub install xiaoyaoclaw-kb-retriever

# Or manual from GitHub
git clone https://github.com/dtsola/xiaoyaoclaw-kb-retriever
# Put SKILL.md, references/, scripts/ into your skills directory
```

## Usage

1. Put the skill into OpenClaw's skills directory
2. Prepare your knowledge base: put files into `knowledge/` in your workspace (or point to any path in conversation)
3. Build the index (recommended):

```bash
python scripts/build_index.py knowledge
```

4. Ask your agent: "**query xxx from the knowledge base**" — it will locate the KB, navigate the index, retrieve progressively, and answer with sources.

## 🚀 Quick start (3 steps, 5 minutes)

### Step 1: Install

```bash
clawhub install xiaoyaoclaw-kb-retriever
```

### Step 2: Prepare KB + build index

```
your-workspace/
├── skills/xiaoyaoclaw-kb-retriever/   ← skill directory
└── knowledge/                         ← knowledge base (md/pdf/xlsx)
    ├── data_structure.md              ← index (one command)
    └── <domain-dir>/...
```

```bash
python skills/xiaoyaoclaw-kb-retriever/scripts/build_index.py knowledge
```

### Step 3: Ask

> Query the 2024 sales report key numbers from the knowledge base.

The agent will: read the index → locate relevant files → retrieve progressively → answer with sources.

### Daily habits

| Scenario | Action |
|---|---|
| First-time setup | `python build_index.py knowledge` |
| New files added | re-run build_index (skips existing, `--force` to rebuild) |
| Custom directory | say "use ./docs as the knowledge base" |
| Large PDFs | auto page-range extraction (extract_pdf_text.py), never whole-file |

## Why not a vector RAG?

| | Vector RAG (qmd / boof / hk101) | **xiaoyaoclaw-kb-retriever** |
|---|---|---|
| Dependencies | embedding models / cloud API keys / local ML | ✅ Zero (grep + read + pdfplumber + pandas) |
| Index | vector index build required | ✅ Lightweight text index, one command |
| Privacy | some upload to cloud | ✅ Fully local |
| Platforms | mostly Unix-oriented | ✅ Windows & macOS first-class |
| Language | English-first | ✅ Bilingual (中文 / English) |
| Context cost | loads index/vectors | ✅ Progressive retrieval, only matched windows |

## Directory structure

```
xiaoyaoclaw-kb-retriever/
├── SKILL.md                    # main skill (OpenClaw-adapted)
├── manifest.json               # compat: openclaw / claude-code / cursor / ...
├── references/
│   ├── pdf_reading.md          # PDF handling (unified Python pipeline)
│   ├── excel_reading.md        # Excel reading
│   └── excel_analysis.md       # Excel analysis
├── scripts/
│   ├── build_index.py          # [highlight] one-command data_structure.md generator
│   └── extract_pdf_text.py     # cross-platform PDF text extraction
├── templates/
│   └── data_structure.md       # index template
├── docs/
│   └── DESIGN.md               # design doc
├── README.md / README.en.md
└── LICENSE
```

## Upstream credit

Forked & adapted from [ConardLi/garden-skills](https://github.com/ConardLi/garden-skills) kb-retriever (MIT):
- **Kept**: hierarchical index navigation, learn-before-process, progressive retrieval, sourced answers
- **Adapted**: OpenClaw tool mapping (read / exec dual-platform commands), unified Python PDF pipeline, one-command index builder, bilingual docs

## License

MIT — use freely, attribution optional.

---

## 🛠️ Custom development?

**Agent & Skills customization, from ¥800.**

- WeChat: `dtsola` (note: **openclaw定制**)
- Scope: OpenClaw multi-agent deployment / workspace standardization / custom Skill development / agent memory systems / knowledge-base setup

## Sister projects

- 🏠 **xiaoyaoclaw-workspace-initializer**: give every agent a "home" — standard directory structure + WORKSPACE.md rules + multi-agent config safety. <https://github.com/dtsola/xiaoyaoclaw-workspace-initializer>
- 🧠 **xiaoyaoclaw-memory-distill**: distill conversations into MEMORY.md + daily logs, solve context overflow. <https://github.com/dtsola/xiaoyaoclaw-memory-distill>
- 🗂️ **xiaoyaoclaw-task-progress-tracker**: directory-as-container, PROGRESS.md-as-card — tasks/ & projects/ lifecycle management. <https://github.com/dtsola/xiaoyaoclaw-task-progress-tracker>

## 小遥Claw (XiaoYao Claw)

**Put an AI assistant into your own computer.**

- 🚀 Landing page: <https://www.yuque.com/dtsola/igp1aa/adcicbai2zlem0bz>
- 📖 Intro: <https://github.com/dtsola/xiaoyaoclaw-introduction>

## About the author

- 🌐 Blog: <https://www.dtsola.com>
- 📺 Bilibili: <https://space.bilibili.com/736015>
- 💻 GitHub: <https://github.com/dtsola>
- 📕 Xiaohongshu: <https://www.xiaohongshu.com/user/profile/5b4c0597e8ac2b06aa13346d>

## 💬 Join the community

XiaoYao product family user group — feedback · usage · feature requests:

<p align="center">
  <img src="./assets/readme/community-qr.png" width="280" alt="XiaoYao AI user group QR code: scan to join, or add WeChat dtsola (note: 加群)">
</p>

<p align="center">Scan to join, or add WeChat <code>dtsola</code> (note: <b>加群</b>)</p>
