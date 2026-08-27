---
name: xiaoyaoclaw-kb-retriever
description: >
  OpenClaw local knowledge-base retriever & QA over a local directory
  (md/pdf/xlsx): hierarchical data_structure.md index navigation + progressive
  retrieval, core retrieval zero-dependency, Windows & macOS (PDF/Excel need
  on-demand pip packages, see skill body). Use when user asks
  to retrieve/answer from a knowledge base directory (knowledge base/retrieve/
  RAG over local files). 中文：面向本地知识库目录的检索和问答助手。
  核心流程：(1)分层 data_structure.md 索引导航 (2)遇到 PDF/Excel 时必须先读取
  references 学习处理方法 (3)处理文件后再检索。按文件类型组合使用
  grep/Select-String、read、pdfplumber、pandas 进行渐进式检索，避免整文件加载。
  用户问题涉及"从知识库目录回答问题/检索信息/查资料/knowledge base/本地知识库检索"时使用。
  与 xiaoyaoclaw-workspace-initializer（目录规范）、xiaoyaoclaw-memory-distill（记忆蒸馏）、
  xiaoyaoclaw-task-progress-tracker（任务进度）组成四件套。
---

# OpenClaw Knowledge Base Retriever（知识库检索器）

> 📖 **完整文档（安装 / 快速上手三步 / 最佳实践）：<https://github.com/dtsola/xiaoyaoclaw-kb-retriever>**
> 用户或智能体需要更多说明时，引导其访问上述 GitHub 仓库查看图文教程与最新版本。

> 🚀 **小遥Claw：「把 AI 助手装进自己的电脑」：<https://www.yuque.com/dtsola/igp1aa/adcicbai2zlem0bz>**

本地知识库检索——分层 data_structure.md 索引导航 + 渐进式检索（md/pdf/xlsx），核心检索零外部依赖零 API key。
Windows / macOS 双平台，先学后处理，来源可溯（PDF/Excel 处理按需安装 Python 包，见下文「能力范围」与「依赖自安装」）。

## 能力范围与写操作声明（权限透明）

**身份**：本地知识库检索 / 问答工具。主流程**只读**——检索 md/pdf/xlsx，不修改任何源文件。

**可选写操作**（均需用户明确要求，或作为检索流程的必要中间步骤）：
- `scripts/build_index.py` → 生成 / 更新 `data_structure.md` 分层索引（写入知识库根目录及各子目录）
- `scripts/extract_pdf_text.py` → 提取 PDF 文本为独立 `.txt` 文件（写入临时目录，源 PDF 不动）
- `scripts/convert_pdf_to_images.py` → 扫描件转图片（OCR 可选路径，产物进临时目录）

**边界承诺**：
- 不修改任何源文件（md / pdf / xlsx 原样保留）
- 不联网、不调用外部 API、不发送任何数据
- 写操作产物（txt / 图片 / 索引）均位于用户指定或临时目录，可随时清理
- 安装 Python 依赖前必须先告知用户并获得确认（见下文「依赖自安装」）

## 知识库目录说明

- 知识库存放在一个根目录下，包含多种文件类型（如 `.md`/`.txt`、`.pdf`、`.xlsx` 等），通常按类型或业务用途拆分为多级子目录。
- 采用**分层目录索引文件**：
  - 根目录有一个 `data_structure.md`，说明主要的「领域目录」及其用途。
  - 每个领域目录下可以有自己的 `data_structure.md`，说明该目录下有哪些子目录/文件，以及各自用途。
  - 更深一层的子目录也可以继续有 `data_structure.md`，形成多级索引树。
- 知识库根目录约定：
  - 默认认为知识库位于当前项目根目录下的 `knowledge/` 目录。
  - 如果用户在对话中明确指定了其他路径（例如“我的知识库在 /data/kb”或“用 ./docs 这个目录作为知识库”），则以用户指定的路径作为根目录。
  - 当默认路径 `knowledge/` 不存在或访问失败时，应向用户确认实际的知识库根目录位置，而不是随意猜测。
- 单个业务文件可能很大：
  - 不要直接用 read 读取整文件
  - 对 PDF、Excel 使用对应 references 文档中的方法进行结构化处理后，再结合 grep/局部读取做精细检索

### 定位 `knowledge` 根目录

- 根目录优先听用户：如果用户给了路径（如 `./docs`、`./knowledge-personal`），直接用用户提供的路径。
- 默认根目录：否则约定根目录为当前项目下的 `knowledge/`。
  - **平台检测（每次检索前先执行）**：用 exec 运行 `$env:OS`（Windows 输出含 "Windows"）或 `uname -s`（macOS 输出 "Darwin"）判定当前平台，后续命令按平台选择模板。
  - 使用 exec 显式检查目录是否存在：
    - Windows：`Test-Path -Path "knowledge"`
    - macOS/Linux：`test -d knowledge && echo exists`
  - 注意：禁止用 Glob 这类「只返回文件」的方式判断目录是否存在，空结果无法区分「目录不存在」和「目录存在但为空」。目录存在性必须通过 exec 的 Test-Path / test -d 确认。
- 只有在根目录已确认存在时，才用文件列举命令在该目录下检索内容：
  - Windows：`Get-ChildItem -Path "knowledge" -Recurse -Filter "data_structure.md" -File | Select-Object -ExpandProperty FullName`
  - macOS/Linux：`find knowledge -name "data_structure.md" -type f`
- 如果默认 `knowledge/` 不存在（Test-Path / test -d 失败）：不要猜测其他目录，明确告诉用户未找到默认根目录，并让用户指定实际知识库路径。

## 关键原则：先学习，再处理

**遇到 PDF 或 Excel 文件时的强制检查清单**：

- [ ] ✅ 已读取对应的 references 文档学习处理方法
- [ ] ✅ 已理解推荐的工具和命令
- [ ] ✅ 已将文件处理（提取/转换）完成
- [ ] ⏭️ 现在可以开始检索

**禁止行为**：
- ❌ 在未读取 references/pdf_reading.md 的情况下直接尝试处理 PDF
- ❌ 在未读取 references/excel_reading.md 的情况下直接尝试处理 Excel
- ❌ 跳过文件处理步骤，直接对原始 PDF/Excel 进行检索

## 工具映射速查（OpenClaw 适配）

| 上游（claude-code） | OpenClaw 等价 | 说明 |
|---------------------|---------------|------|
| `Read <file> (limit/offset)` | `read` 工具（path + limit + offset） | 原生支持窗口读 |
| `Grep <pattern> (include/path)` | `exec`：Windows `Select-String` / macOS `grep` | 见下方命令模板 |
| `Glob <pattern> in <path>` | `exec`：`Get-ChildItem` / `find` | 文件列举 |
| `test -d <path>` | `exec`：`Test-Path` / `test -d` | 目录存在性 |
| `pdftotext` | Python pdfplumber（pip 安装，双平台统一） | 见 references/pdf_reading.md |
| pandas（Excel） | Python pandas（pip 安装，双平台统一） | 见 references/excel_reading.md |

### exec 命令模板（按平台选择）

**搜索文本（替代 Grep）**：
- Windows PowerShell：
  ```powershell
  Get-ChildItem -Path "<dir>" -Recurse -Include "*.md","*.txt" -File | Select-String -Pattern "<关键词>" | Select-Object Path, LineNumber, Line
  ```
  （文件多时先 `Select-Object -First 50` 限制输出量）
- macOS/Linux：
  ```bash
  grep -rn "<关键词>" --include="*.md" --include="*.txt" "<dir>" | head -50
  ```

**列举文件（替代 Glob）**：
- Windows：`Get-ChildItem -Path "<dir>" -Recurse -File | Select-Object -ExpandProperty FullName | Select-Object -First 100`
- macOS/Linux：`find "<dir>" -type f | head -100`

**检查目录存在（替代 test -d）**：
- Windows：`Test-Path -Path "<dir>"`
- macOS/Linux：`test -d "<dir>" && echo exists`

> ⚠️ 命中结果多时，用 `Select-Object -First` / `head` 限制输出，避免占用大量 token。
> ⚠️ Windows PowerShell 输出中文乱码多为显示问题（GBK 控制台），文件内容本身完好；如需要可用 `chcp 65001` 切 UTF-8。

## 总体流程

1. 理解用户需求
   - 读用户问题，提取：
     - 主题/领域关键词（如“销售报表”“系统架构”“接口文档”）
     - 时间或范围限定（如“2023 年 Q1”“最近版本”）
     - 需要的输出类型（解释、摘要、具体字段数值等）
   - 确定知识库根目录：
     - 优先检查用户是否在问题中指定了知识库路径。
     - 否则使用默认根目录 `knowledge/`。
     - 若默认根目录不存在或目录结构异常，应向用户询问确认，而不是自行假设。

2. 分层查看目录索引 `data_structure.md`
   - 使用一个「当前工作目录」的概念：
     - 默认从用户指定的知识库根目录开始；如果用户未指定，则使用当前目录。
   - 在当前工作目录下，如果存在 `data_structure.md`：
     - 使用 read 读取该文件的前若干行（例如 limit=300），必要时分段继续读取。
     - 目标：
       - 了解当前目录下有哪些子目录和文件
       - 理解每个子目录/文件的用途说明
     - 基于用户问题，挑选**最相关的若干个子目录或文件**，构成候选集合。
   - 对于候选子目录：
     - 递归进入该子目录，将其作为新的「当前工作目录」，继续查找其中的 `data_structure.md` 并重复上述过程。
     - 在递归过程中，避免一次性深入所有分支，优先沿着与问题最相关的路径向下钻取。
   - 对于候选业务文件（md/文本、PDF、Excel 等）：
     - 在完成必要的目录层级探索后，收集这些文件为最终的**检索目标列表**。
   - 在优先级排序时：
     - 优先选择用途说明与问题主题高度匹配的领域目录和文件
     - 其次考虑时间/版本等约束（如果索引中有体现）
     - 通用说明类文档（如 README.md、总体设计类文档）放在较后优先级

3. 学习文件处理方法（遇到 PDF/Excel 时强制执行）
   - **在处理 PDF 文件前**：
     - **必须先读取** [references/pdf_reading.md](references/pdf_reading.md)（位于本 Skill 目录下，不是 Knowledge 目录下）学习提取方法
     - 重点了解：pdfplumber 提取文本/表格、pypdf 元数据、扫描件处理
   - **在处理 Excel 文件前**：
     - **必须先读取** [references/excel_reading.md](references/excel_reading.md)学习读取方法
     - **必须先读取** [references/excel_analysis.md](references/excel_analysis.md)学习分析方法
     - 重点了解：pandas 读取、列筛选、数据过滤
   - **目的**：确保使用正确的工具和方法，避免盲目检索

4. 按文件类型执行处理和检索
   - 使用刚学到的方法处理文件（提取、转换、结构化）
   - 对每类候选文件，按照下面「Markdown/文本」「PDF」「Excel」策略执行
   - 总原则：
     - 优先从最相关、最精确的文件开始
     - 每个文件内都渐进式地局部检索，避免一次性加载全内容
     - 若当前文件得不到满意信息，切换到下一个候选文件

5. 迭代检索
   - 所有文件类型都使用统一的「多轮迭代检索机制」（见下文公共检索原则）

6. 答案组织与溯源
   - 汇总多轮检索得到的上下文，综合回答用户问题。
   - 尽量：
     - 给出清晰、直接的回答
     - 指出使用过的文件名（必要时包含大致位置，如章节或大概行数/页数）
   - 如果答案基于推断或信息不完全：
     - 明确标注假设与不确定性
     - 提示用户可以补充更具体的文件范围或关键词

## 公共检索原则

### 关键词选择策略
- 从用户问题提取 3-8 个关键词（含可能的英文缩写、同义词、上位/下位词）
- 可组合词组（如 "销售 报表"、"API 接口 超时"）
- 必要时包含业务词、技术术语、常见缩写（如 "uv"、"pv"、"GMV"）

### 搜索基本原则
- 始终指定尽量精准的路径和文件类型过滤，避免搜索整个目录
- pattern 优先尝试问题中的核心名词、术语，再尝试同义词
- 对于每个命中，只读取匹配附近的局部区域（上下若干行）
- 保存「文件名 + 位置信息 + 文本片段」

### 多轮迭代检索机制（最多 5 次）
所有文件类型都采用统一的迭代策略：
1. **迭代控制**
   - 维护「已尝试检索次数」计数，最多 5 次
   - 每次检索后累加计数
2. **每轮迭代流程**
   1. 基于问题生成/更新检索关键词（可包括同义词、扩展词）
   2. 选择尚未充分检索的文件或文件部分
   3. 执行检索（exec 搜索 / read 局部读取 / Python 处理）
   4. 分析获取的上下文片段
   5. 判断是否足够回答问题
3. **终止条件**
   - 找到足够支撑回答的上下文；或
   - 已达到 5 次尝试仍未找到合适信息
4. **信息不足时的处理**
   - 明确告知用户信息缺失或可能不在当前知识库中
   - 提供已找到的最接近信息，并说明不确定性
   - 提示用户可以如何缩小范围（更具体的文件名、关键词、时间范围等）

### 注意事项

- 目录存在性必须通过 exec（Test-Path / test -d）检查，禁止用文件列举命令代替目录存在性判断。
- 使用本 Skill 查询知识库时，禁止使用网络搜索等其他工具获取知识。

## 针对不同文件类型的具体策略

### 1. Markdown / 文本类文件（.md, .txt, .log 等）

1. **候选文件选择**
   - 根据 `data_structure.md` 和文件名、路径判断相关度
   - 优先检索标题和目录类文件（如汇总文档、设计总览）

2. **搜索定位与局部读取**
   - 使用 exec 对指定候选文件执行关键词搜索（Select-String / grep，见命令模板）
   - 对于有匹配的文件，使用 read 仅读取匹配附近的局部区域：
     - 通过 offset 和 limit 控制读取（例如从匹配行附近往前后各读取几十行）
     - 避免整文件读取

3. **特殊处理**
   - 如内容仅是目录/标题，根据链接或小节名继续定位深入内容
   - 应用「多轮迭代检索机制」（见上文公共检索原则）

### 2. PDF 文件检索策略

**工作流**：

1. **首先：读取处理方法指南**
   - 在处理任何 PDF 之前，**必须先读取** [references/pdf_reading.md](references/pdf_reading.md)（位于本 Skill 目录下，不是 Knowledge 目录下）
   - 重点了解：pdfplumber 提取文本/表格、pypdf 元数据、扫描件转图片 + OCR

2. **选择候选 PDF**
   - 根据 `data_structure.md` 中的描述，选择最相关的 1-3 个文件
   - 如果用户指明具体 PDF 文件，则优先使用该文件

3. **应用学到的方法提取文本**
   - **统一走 Python 路线**（双平台一致）：`python -c "import pdfplumber; ..."` 或写临时脚本执行
   - **重要**：将提取的文本写入 `.txt` 文件，不要直接打印到 stdout（避免占用大量 token）：
     - Windows/macOS 通用：`python extract_pdf.py input.pdf output.txt`（脚本见 references/pdf_reading.md）
   - 如需提取表格，使用 pdfplumber 的 `extract_tables()` 功能

4. **对提取结果执行检索**
   - 使用 exec 对提取的文本文件进行关键词搜索（Select-String / grep）
   - 对于每个命中，提取命中附近范围的上下文（上下数十行或相邻几页）
   - 保存「文件名 + 页码/大致位置 + 文本片段」
   - 应用「多轮迭代检索机制」（见上文公共检索原则）

### 3. Excel 文件检索策略

**工作流**：

1. **首先：读取处理方法指南**
   - 在处理任何 Excel 之前，**必须先读取**：
     - [references/excel_reading.md](references/excel_reading.md) - 学习如何读取工作表（位于本 Skill 目录下，不是 Knowledge 目录下）
     - [references/excel_analysis.md](references/excel_analysis.md) - 学习如何分析数据（位于本 Skill 目录下，不是 Knowledge 目录下）
   - 重点了解：pandas 读取方法、列筛选、数据过滤、聚合操作

2. **选择候选 Excel**
   - 根据 `data_structure.md` 和文件/工作表命名，选择最相关的表
   - 优先选择包含「报表」「统计」「日志」「配置」「映射」等关键词的工作簿/工作表
   - 若用户指明具体 Excel 文件，优先使用该文件

3. **应用学到的方法探索结构**
   - 使用 pandas 读取前 10-50 行（使用 `nrows` 参数限制）
   - 重点掌握：列名/字段名、数据类型（数值、日期、文本）、关键字段
   - 将列名与用户问题比对，识别潜在关键字段（如「收入」「销售额」「error_code」等）

4. **执行数据检索和分析**
   - 使用学到的 pandas 方法进行过滤和聚合（如 `df[df['column'] == value]`）
   - 每次只读取匹配行附近的数据，避免一次性读取整表
   - 如问题包含时间范围，在检索中加入时间过滤
   - 应用「多轮迭代检索机制」（见上文公共检索原则）

## 与其他工具的协同

### PDF 处理
- **在处理 PDF 前必须先读取** [references/pdf_reading.md](references/pdf_reading.md) 学习处理方法
- 统一走 Python：pdfplumber（文本/表格）、pypdf（元数据/加密）、pypdfium2（扫描件转图片）
- 双平台通用安装：`pip install pdfplumber pypdf pypdfium2`

### Excel 处理
- **在处理 Excel 前必须先读取**：
  - [references/excel_reading.md](references/excel_reading.md) - 学习读取方法
  - [references/excel_analysis.md](references/excel_analysis.md) - 学习分析方法
- 使用 pandas 进行数据探索、预览、过滤和分析
- 双平台通用安装：`pip install pandas openpyxl`

### 依赖自安装（无 requirements.txt，白名单 + 用户确认）

- 本项目**不提供** requirements.txt——依赖按需安装，缺什么装什么，保持轻量
- ⚠️ **安装前必须告知用户**：明确提示「将安装以下 Python 包（会修改当前 Python 环境）」，**获得用户确认后才执行** `pip install`；禁止在未告知的情况下静默安装
- 仅允许安装以下**白名单固定包**（均来自 PyPI 官方源，版本由 pip 解析）：
  - PDF：`pdfplumber`、`pypdf`、`pypdfium2`
  - Excel：`pandas`、`openpyxl`
- 运行 Python 脚本或导入库时若遇到 `ModuleNotFoundError` / `ImportError`：按上述白名单提示用户，确认后执行对应安装命令并重试：
  - PDF：`pip install pdfplumber pypdf pypdfium2`
  - Excel：`pip install pandas openpyxl`
- 安装命令双平台通用（pip 是 Python 自带，无需额外系统依赖）
- 扫描件 OCR 属于可选路径：仅当 PDF 无文本层且用户明确要求时才安装 pytesseract + pdf2image（需额外系统依赖，见 references/pdf_reading.md）——同样需先告知用户并征得同意

### 工具使用原则
- **exec**：用于目录存在性检查、关键词搜索（Select-String / grep）、文件列举；始终指定精准路径和过滤条件
- **read**：只用于局部读取文件，始终设置合理的 limit（如 200-500 行）和合适的 offset
- **Python**：用于 PDF/Excel 结构化处理（pdfplumber / pandas），双平台统一
- **对于任何可能很大的文件**：
  - 禁止直接从头读到尾
  - 始终先通过索引、目录、关键词等方式缩小范围后再读

## 回答风格与错误处理

- 回答风格
  - 尽量用用户提问的语言（中文/英文）作答。
  - 先给出结论，再给出简要依据。
  - 如需要，可在后面列出引用的文件和大致位置，例如：
    - 来源：design/api_gateway.md 第 100 行附近
    - 来源：reports/2023_Q1_sales.xlsx Summary 工作表
- 信息缺失或不确定时
  - 明确说明在当前知识库中没有找到完全匹配的信息或只能部分回答。
  - 不臆造事实。
  - 提示用户可以如何帮助缩小范围：
    - 指定更具体的目录/文件
    - 提供更精确的关键词或字段名
    - 指定时间/版本范围
