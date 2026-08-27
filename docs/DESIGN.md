# DESIGN.md — xiaoyaoclaw-kb-retriever 改造方案 A

> 项目：OpenClaw Knowledge Base Retriever（知识库检索器）
> 上游：github.com/ConardLi/garden-skills/tree/main/skills/kb-retriever（MIT，★11098）
> 日期：2026-08-27 | 状态：已确认（指挥官拍板）

## 1. 定位

OpenClaw 版本地知识库检索 skill：分层索引导航 + 渐进式检索 + 多格式（md/pdf/xlsx），
**零外部依赖、零索引构建、零 API key**——生态里唯一满足「轻量 + 中文 + 无依赖」的方案
（竞品 qmd/local-file-rag/boof/hk101 均需运行时或云端 embedding，见调研报告）。

四件套定位：**家（initializer）→ 内容（memory-distill）→ 状态（tracker）→ 知识（kb-retriever）**

## 2. 命名

| 维度 | 值 |
|------|-----|
| 项目 slug | `xiaoyaoclaw-kb-retriever` |
| README 英文标题 | OpenClaw Knowledge Base Retriever |
| 中文名 | 知识库检索器 |
| GitHub | dtsola/xiaoyaoclaw-kb-retriever（public, main, MIT） |
| ClawHub | slug `xiaoyaoclaw-kb-retriever` @dtsola |

## 3. 目录结构（目标）

```
xiaoyaoclaw-kb-retriever/
├── SKILL.md                      # 主技能（OpenClaw 适配版，中英触发）
├── manifest.json                 # compat 加 openclaw
├── README.md / README.en.md      # 双语（对齐三件套结构）
├── references/                   # 保留上游：pdf_reading / excel_reading / excel_analysis
├── scripts/
│   ├── build_index.py            # 【新增】自动扫描生成 data_structure.md 骨架
│   └── convert_pdf_to_images.py  # 保留上游：扫描件兜底
├── templates/
│   └── data_structure.md         # 【新增】索引文件模板（上手门槛↓）
└── assets/readme/                # 【新增】hero.svg + 群二维码（对齐三件套 README 视觉）
```

## 4. 改造点清单

### M1 工具名适配（核心，0.5 天）

上游面向 claude-code/cursor（`Read`/`Grep`/`Glob` 工具），OpenClaw 下不可用。映射规则：

| 上游指令 | OpenClaw 适配 | 说明 |
|----------|---------------|------|
| `Read <file> (limit/offset)` | `read` 工具（原生支持 offset/limit） | 天然兼容 |
| `Grep <pattern> (include/path)` | `exec` 执行 grep（Unix）或 Select-String（Windows） | 平台分支 |
| `Glob <pattern> in <path>` | `exec` 执行 Get-ChildItem -Recurse（Windows）/ find（Unix） | 平台分支 |
| `test -d knowledge` | `exec` Test-Path（Windows）/ test -d（Unix） | 平台分支 |
| pdftotext | pdftotext，缺失时降级 pdfplumber（pip） | 检测 + 兜底 |

**平台策略**：**Windows + macOS 双平台一等公民**（指挥官要求，2026-08-27）。
- SKILL.md 内置「平台检测」步骤：agent 先判定 OS（Windows → PowerShell 命令；macOS → bash/zsh 命令），再选择对应命令模板
- 所有 exec 命令一律给出双平台版本（PowerShell / bash 并列），禁止只写单一 shell
- 工具选择不依赖单一 shell：grep 用 `Select-String`（Win）/ `grep`（Mac）；目录存在性用 `Test-Path`（Win）/ `test -d`（Mac）；文件列举用 `Get-ChildItem`（Win）/ `find`（Mac）
- README / references / scripts 中涉及命令处全部双平台标注

### M2 manifest + description（0.25 天）

- compat 追加 `openclaw`
- category: "Retrieval / Local Knowledge Base"
- description 中英双触发：知识库检索 / 查资料 / 从知识库回答问题 / knowledge base / retrieve / RAG over local files

### M3 build_index.py（差异化亮点，0.25 天）

自动扫描知识库目录 → 生成 data_structure.md 骨架：
- 遍历目录树，提取每个目录的用途（README 首段 / 文件名聚类 / 空模板）
- 输出符合上游索引规范的分层 data_structure.md
- 用法：`python build_index.py <kb-root>`，幂等（已有索引则只补缺）

### M4 实测 + 发布（0.25 天）

1. 本地真实知识库（本工作区 knowledge/）全链路 QA：md/pdf/xlsx 各一例 + 中英问答
2. GitHub 建仓 + push（走代理 22307；直连可用则直连）
3. ClawHub 提交 v1.0.0
4. 全局技能同步 state/skills/xiaoyaoclaw-kb-retriever/
5. 三件套 README 互链（姊妹项目表补 kb-retriever）+ 本项目 README 链三件套

## 5. 保留上游精华（不动）

- 分层 data_structure.md 索引树导航
- 先学后处理（PDF/Excel 强制读 references 再动手）
- 渐进式检索（grep 定位 → 窗口读 → 最多 5 轮迭代）
- 默认根目录 `knowledge/`（与 initializer 目录规范天然对齐）
- 回答带来源溯源（文件 + 位置）

## 6. 里程碑

| 里程碑 | 内容 | 产出 |
|--------|------|------|
| M1 | 工具名适配 + manifest | SKILL.md 改造版 + manifest.json |
| M2 | description 双语触发 | frontmatter 完成 |
| M3 | build_index.py + 模板 | scripts/ + templates/ |
| M4 | 实测 + 发布 | GitHub + ClawHub + 全局技能 + 互链 |

总计约 1 天。

## 7. 风险与对策

| 风险 | 对策 |
|------|------|
| Windows 无 pdftotext / macOS 无 poppler | pdfplumber 兜底 + 检测脚本（双平台统一走 pip） |
| 上游大文件检索仍耗 token | 保留窗口读约束，README 强调 |
| 中文编码坑（Windows PowerShell 5.1 控制台） | 脚本用 Python 写 UTF-8，命令模板避免内联中文；macOS 无此问题 |
| 双平台命令差异导致行为漂移 | SKILL.md 强制「平台检测 → 命令模板」两步，README 提供双平台快速上手 |

## 8. 参考

- 调研报告：tasks/skills-gap-research/FINAL_知识库场景调研报告.md
- 上游：github.com/ConardLi/garden-skills（MIT）
- 三件套 README 结构对齐对象：xiaoyaoclaw-memory-distill / xiaoyaoclaw-task-progress-tracker
