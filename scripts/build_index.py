# -*- coding: utf-8 -*-
"""自动扫描知识库目录，生成/补齐 data_structure.md 分层索引骨架。

用法:
    python build_index.py <kb-root> [--force]

说明:
    - 遍历 <kb-root> 下的目录树，为每个含内容的目录生成/补齐 data_structure.md
    - 已存在 data_structure.md 的目录默认跳过（--force 时覆盖重建）
    - 目录用途推断来源：README.md 首段 / 文件名聚类 / 目录名
    - 输出符合 kb-retriever 索引规范（Purpose / Files / Coverage 三段式）
    - Windows / macOS 双平台通用（纯 Python，无外部依赖）

示例:
    python build_index.py knowledge            # 为 knowledge/ 生成索引
    python build_index.py knowledge --force    # 全部重建
"""
import argparse
import os
import sys

INDEX_NAME = "data_structure.md"
README_NAME = "README.md"
TEXT_EXTS = {".md", ".txt", ".log", ".markdown"}
DOC_EXTS = {".pdf", ".xlsx", ".xls", ".docx", ".csv", ".json", ".yaml", ".yml"}
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".obsidian", ".idea", ".vscode"}


def infer_purpose(directory):
    """从 README 首段 / 目录名推断用途描述。"""
    readme = os.path.join(directory, README_NAME)
    if os.path.isfile(readme):
        try:
            with open(readme, "r", encoding="utf-8-sig") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        return line[:120]
        except Exception:
            pass
    # 回退：目录名
    name = os.path.basename(directory) or directory
    return f"{name} 相关文档与数据"


def scan_directory(directory):
    """扫描目录，返回 (子目录列表, 业务文件列表)。"""
    subdirs, files = [], []
    try:
        entries = sorted(os.listdir(directory))
    except OSError as e:
        print(f"  跳过不可读目录 {directory}: {e}", file=sys.stderr)
        return [], []
    for entry in entries:
        if entry.startswith("."):
            continue
        full = os.path.join(directory, entry)
        if os.path.isdir(full):
            if entry not in SKIP_DIRS:
                subdirs.append(entry)
        elif os.path.isfile(full):
            ext = os.path.splitext(entry)[1].lower()
            # README / 索引文件是说明文件，不作为业务文件列出
            if entry in (INDEX_NAME, README_NAME):
                continue
            if ext in TEXT_EXTS or ext in DOC_EXTS:
                files.append(entry)
    return subdirs, files


def format_size(path):
    try:
        size = os.path.getsize(path)
        if size >= 1024 * 1024:
            return f"{size / 1024 / 1024:.1f}MB"
        if size >= 1024:
            return f"{size / 1024:.0f}KB"
        return f"{size}B"
    except OSError:
        return "?"


def generate_index(directory, subdirs, files):
    """生成 data_structure.md 内容。"""
    name = os.path.basename(directory) or directory
    lines = [f"# {name}", ""]
    lines.append("## Purpose")
    lines.append(infer_purpose(directory))
    lines.append("")
    lines.append("## Files")
    if not subdirs and not files:
        lines.append("- （空目录）")
    for sub in subdirs:
        lines.append(f"- {sub}/ — 子目录，详见其 data_structure.md")
    for fname in files:
        full = os.path.join(directory, fname)
        ext = os.path.splitext(fname)[1].lower()
        kind = "PDF 文档" if ext == ".pdf" else ("表格数据" if ext in (".xlsx", ".xls") else "文本/Markdown")
        lines.append(f"- {fname} — {kind}（{format_size(full)}）")
    lines.append("")
    lines.append("## Coverage")
    lines.append("（待补充：时间范围 / 版本 / 来源说明）")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="生成知识库 data_structure.md 分层索引")
    parser.add_argument("kb_root", help="知识库根目录")
    parser.add_argument("--force", action="store_true", help="覆盖已有索引")
    args = parser.parse_args()

    root = os.path.abspath(args.kb_root)
    if not os.path.isdir(root):
        print(f"错误: 目录不存在 {root}", file=sys.stderr)
        sys.exit(1)

    generated, skipped, empty = 0, 0, 0
    for dirpath, dirnames, filenames in os.walk(root):
        # 跳过隐藏目录与 SKIP_DIRS
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in SKIP_DIRS]
        if dirpath != root and os.path.basename(dirpath).startswith("."):
            continue

        subdirs, files = scan_directory(dirpath)
        if not subdirs and not files:
            empty += 1
            continue

        index_path = os.path.join(dirpath, INDEX_NAME)
        if os.path.exists(index_path) and not args.force:
            skipped += 1
            print(f"跳过（已有索引）: {os.path.relpath(index_path, root)}")
            continue

        content = generate_index(dirpath, subdirs, files)
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(content)
        generated += 1
        rel = os.path.relpath(index_path, root)
        print(f"生成: {rel}（{len(subdirs)} 子目录, {len(files)} 文件）")

    print(f"\n完成: 生成 {generated}，跳过 {skipped}，空目录 {empty}")
    if generated == 0 and skipped == 0:
        print("提示: 知识库为空，或所有目录均无业务文件。")


if __name__ == "__main__":
    main()
