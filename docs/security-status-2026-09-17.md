# ClawHub 安全检查核查与修复（2026-09-17）

> 执行人：天桐｜指令：指挥官「处理 OpenClaw Knowledge Base Retriever」
> 命令：`clawhub skill verify xiaoyaoclaw-kb-retriever`（对象 v1.0.2）

---

## 1. 结论

`ok:false` / `decision:fail` / 原因码 `security.status_not_clean`；`security.status = suspicious`（confidence high）。
**共 13 条**：aig **2**（T09 **error / High** 命令注入 + T08 warning 依赖未钉版）+ skillspector **11**（HIGH 3 / MEDIUM 4 / LOW 4，风险分 91）。

LLM 判词：*"its search instructions use raw shell command templates with user-influenced paths and keywords, which creates a real review concern."*

---

## 2. 命中与修复对照

### 2.1 aig（2 条，都是真问题）

| 命中 | 位置 | 问题 | 修复 |
|---|---|---|---|
| **T09 error（High）** | `SKILL.md:100-115` | **命令注入**：检索模板把**用户关键词与目录**直接写进 shell 字符串（`Select-String -Pattern "<关键词>"` / `grep "<关键词>"`），文本里的引号、反引号、`$()`、`;` 会被 shell 解析 | ① **新增 `scripts/search_kb.py`**（安全检索）：关键词与目录走 **argv 传参**（不经 shell）、按**字面量**匹配（不当正则）、结果条数/单文件大小/扫描范围全有上限、**不写任何文件**；SKILL.md 把它定为**首选**做法 ② 保留 shell 兜底但写死三条规则：变量先行不拼字符串、`-SimpleMatch`/`grep -F`+`-LiteralPath`、**禁止** `iex`/`eval`/`sh -c` 与把用户文本放进命令名·参数名·重定向目标等结构性位置 |
| **T08 warning** | `SKILL.md:302` | 依赖按需 `pip install`，版本未钉 | 新增 **`requirements-optional.txt`**：**精确钉版**（`pdfplumber==0.11.10` / `pypdf==6.19.0` / `pypdfium2==5.13.0` / `pandas==3.0.5` / `openpyxl==3.1.5`；OCR 组 `pytesseract==0.3.13` / `pdf2image==1.17.0` 同样给出钉版）；SKILL.md 依赖章节改为「钉版清单 + 安装前必须告知并取得确认 + 升级须显式改清单」 |

### 2.2 skillspector（11 条）

| 类别 | 条数 | 位置 | 修复 |
|---|---|---|---|
| **TP4** 描述与实际不符（HIGH） | 3 | `SKILL.md:1` | 技能被当成"只读检索"，但实际带**写操作**（生成 `data_structure.md` 索引、PDF 转文本）→ **description 明确写出这两项写操作及触发条件**；SKILL.md 新增「**读写范围与权限**」章节：默认只读；两项可写操作必须由用户点名并确认；写前打印目标路径；只写知识库根目录内、不删文件；并把**权限逐项对应**（Read/Glob/Grep/Bash 检索用，Write/Edit 仅用于这两项） |
| **LP3** 权限未声明（MEDIUM） | 1 | `SKILL.md:1` | frontmatter 补 **`allowed-tools`**（Read/Glob/Grep/Bash/Write/Edit）；`manifest.json` 补 **`permissions`** 段（read/write/network:none/environment:none + 「无 cron/守护/状态文件，写入不出知识库根目录，不删文件」） |
| **SDI-1 ×2 / SDI-4** 脚本意图与声明不符（MEDIUM/LOW） | 3 | `scripts/build_index.py:107`、`:2`、`scripts/extract_pdf_text.py:34` | 由上面 description/manifest 对齐解决；同时给两个脚本加 docstring 明确「**可选维护脚本**，写入什么、需用户确认」 |
| **SQP-3** 语言中立 | 3 | `references/excel_reading.md:1`、`references/excel_analysis.md:1`、`scripts/build_index.py:2` | 三个文件补「**语言可选**」说明；`scripts/search_kb.py` / `extract_pdf_text.py` / `convert_pdf_to_images.py` 同样补上 |
| **SQP-2** OCR 环节缺确认要求 | 1 | `references/pdf_reading.md:177` | SKILL.md 依赖章节明确：**OCR 走同一道确认**（pip 包 + 系统级 tesseract/poppler 都要先讲清影响再执行）；`pdf_reading.md` 已有 OCR 章节，与主文档口径统一 |

### 2.3 脚本层加固（顺带做的，属同一信任边界）

- **`scripts/extract_pdf_text.py`**：新增 `resolve_within()` —— 输出 `.txt` **必须与源 PDF 同目录**，否则拒绝；写前打印披露
- **`scripts/convert_pdf_to_images.py`**：新增模块 docstring（写盘披露 + 依赖/系统依赖说明）+ `resolve_output_within()` —— 输出目录**必须落在源 PDF 目录树内**
- **`scripts/build_index.py`**：写前打印「将在哪些目录写入 `data_structure.md`」；新增 `commonpath` 双保险，防止异常路径/符号链接越界写入

**包内容卫生**：新增 `.clawhubignore` 排除 `PROGRESS.md` / `docs/` → 包内 **16 个文件**（新增 `requirements-optional.txt` 与 `search_kb.py`）。

---

## 3. 验证（真跑，全部 PASS）

测试脚本 `tmp/kb_test.py`：

1. **语法**：4 个脚本 `py_compile` 全通过
2. **安全检索**：`search_kb.py <kb> alpha` 正确命中 `docs/intro.md` 与 `notes.txt`；打印检索范围
3. **注入样式关键词**：`x"; rm -rf __nope__; echo "pwned` 作为关键词 → 退出码 0、**无 pwned 输出、文件未被删除**（argv 传参 + 字面量匹配，无 shell 解析）
4. **目录不存在** → 明确报错退出码 2
5. **`--list`** 只列 md/txt（默认扩展名生效）
6. **索引生成**：`build_index.py` 生成 3 个 `data_structure.md`（三段式 Purpose/Files/Coverage 齐全）、**打印写盘披露**、**`README.md` 未被改写**
7. **幂等**：第二次运行全部跳过已有索引
8. **路径约束**：`extract_pdf_text.resolve_within()` —— 同目录输出**通过**、`C:/Windows/System32/out.txt` **被拒绝**

附加：`hero.svg` 清注释后中文副标题改双语。

---

## 4. 待办

- [ ] 发 **v1.0.3** → 等扫描 → 复扫核对 13 条（重点看 error 级命令注入）
- [ ] GitHub 推送（代理 22307 未监听 + 直连超时）

## 5. 原始证据

- `docs/evidence/verify-v1.0.2-2026-09-17.json`
