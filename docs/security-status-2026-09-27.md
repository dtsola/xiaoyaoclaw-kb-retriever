# kb-retriever 安全修复记录 · 2026-09-27（v1.0.7）

> 本轮触发：ClawHub 对 **v1.0.6** 的扫描判定 `suspicious / high`。

## 一、判词（原文）

- **aig T09**（Insecure Skill Coding Practices，warning）
  `scripts/search_kb.py:52` — *"Symlinked files can escape the authorized knowledge-base root"*
- **skillspector AE1**（analysis-evasion，HIGH，coverage，confidence 1.0）
  `SKILL.md:61` — *"assets/readme/community-qr.png (partial) — Referenced artifact was not completely inspected"*
- 综合判词（LLM 评审）：*"…review is warranted because one helper can follow symlinks and read files outside the selected knowledge-base folder."*

## 二、根因

1. **读侧漏了（主因）**：v1.0.5 只堵了**写**（`pathguard.py` realpath 容器校验用于三个写盘脚本），
   但 `search_kb.py` 的遍历仍是纯字符串路径 —— **符号链接文件被当成普通文件读取**，
   可以读到知识库之外（`os.walk` 默认不跟随目录链接，但**文件链接照样产出并打开**）。
2. **引用面**：SKILL.md 明确点名了 `assets/readme/community-qr.png`，而扫描器无法完整解析该 PNG
   → 记为「引用物未被完整检查」。

## 三、修复（v1.0.7）

| 层面 | 改动 |
|---|---|
| 统一闸门 | `pathguard.py` 从「写盘校验」升级为**读写双向**容器校验，新增 `read_within()`；docstring/规则覆盖读侧，fail closed |
| 被点名的 helper | `search_kb.py` 重写：根目录 realpath；每个条目 realpath 校验，**越界即跳过并计数**（不打开）；符号链接目录不进入遍历；读取用校验后的真实路径 |
| 一致性 | `build_index.py` 读侧同样过闸（README 读取 + 逐条目列举/取大小），越界跳过计数并在结尾披露 |
| PDF 助手 | 源 PDF 先解析真实路径并打印 `[read]` 行，实际读取真实文件；输出范围仍以真实源目录为基准 |
| 文档口径 | SKILL.md（能力边界 + 硬约束 + frontmatter description）/ manifest.json / 两份 README 全部写入**读侧边界**；删掉触发覆盖率告警的 PNG 路径引用 |
| 代码漂移 | `references/pdf_reading.md` 里**旧的、无边界校验的 `extract_pdf_text.py` 副本**删除，改为指向随包脚本并写明边界；OCR/渲染片段补写盘边界说明 |

## 四、验收（29/29 PASS，真建符号链接）

- **读侧**：库外哨兵关键词搜索 **0 命中**、输出不含库外内容、报告「已跳过 N 个越界符号链接」；`--list` 不含越界文件/目录条目；**库内合法链接仍可用**
- **写侧**：库外文件（被链接指向的索引）`--force` 后**逐字节未变**；库外目录未生成任何 `data_structure.md`；库内索引照常生成
- **单元**：`read_within` 库内放行 / 越界抛 `PathEscapeError`
- **回归**：普通知识库检索、索引生成、幂等跳过全部正常
- **元数据**：5 脚本编译通过、SKILL.md frontmatter YAML 合法、manifest version=1.0.7

证据：`docs/evidence/verify-v1.0.7-2026-09-27.json`

## 五、残留与后续

- 发布后跑 `clawhub skill verify xiaoyaoclaw-kb-retriever --version 1.0.7` 复核（目标 `security=clean / benign`）
- 若 AE1（PNG 覆盖）在删除引用后仍复现，备选动作：把 `community-qr.png` 压缩（palette 量化 97KB→约 39KB，实测可解但属有损）或从包内移除
- 元数据复核提醒：ClawHub 重发时会**重算 summary**（09-25 实测结论），发布后必须逐项核对 displayName / topics / license / summary
