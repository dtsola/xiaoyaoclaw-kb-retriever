# -*- coding: utf-8 -*-
"""双平台通用 PDF 文本提取（pdfplumber）。

用法:
    python extract_pdf_text.py <input.pdf> <output.txt> [start_page] [end_page]

示例:
    python extract_pdf_text.py doc.pdf doc.txt          # 全部页
    python extract_pdf_text.py doc.pdf doc.txt 1 5      # 第 1-5 页

说明:
    - Windows / macOS 行为一致（纯 Python，无 poppler 依赖）
    - 输出写入文件而非 stdout，避免占用 LLM token

安全边界 / Safety:
    - **写盘披露**：本脚本会新建/覆盖 <output.txt>（仅此一个文件，源 PDF 不动）；
      运行前会打印将写入的绝对路径。
    - **写入范围**：<output.txt> 必须与 <input.pdf> 位于同一知识库根目录内，
      不得写到系统目录或越出该根目录；**按真实路径校验**（`scripts/pathguard.py`，
      解符号链接后仍须在根内，越界即拒绝）
    - **本操作需用户点名并确认**：把 PDF 转成文本文件属派生写入，不是纯检索。

语言 / Language：输出默认中文，**语言可选**（可按用户语言调整文案）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pathguard  # noqa: E402

import pdfplumber  # 可选依赖，版本见 requirements-optional.txt


def resolve_within(pdf_path: str, out_path: str) -> str:
    """校验输出路径：解析符号链接后，仍必须与源 PDF 同处一个（真实）根目录内。"""
    root = pathguard.real_root(os.path.dirname(os.path.abspath(os.path.expanduser(pdf_path))))
    resolved = pathguard.real_target(out_path)
    if not pathguard.is_within(root, resolved) or resolved == root:
        print(
            f"ERROR: 输出文件必须与源 PDF 位于同一目录内（{root}），已拒绝：{out_path} -> {resolved}",
            file=sys.stderr,
        )
        sys.exit(2)
    return resolved


def main():
    if len(sys.argv) < 3:
        print(
            "用法: python extract_pdf_text.py <input.pdf> <output.txt> [start_page] [end_page]",
            file=sys.stderr,
        )
        sys.exit(1)
    input_pdf, output_txt = sys.argv[1], sys.argv[2]
    start = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    end = int(sys.argv[4]) if len(sys.argv) > 4 else None

    output_txt = resolve_within(input_pdf, output_txt)
    print(f"[write] 将写入派生文本文件：{output_txt}（源 PDF 不改动）")

    with pdfplumber.open(input_pdf) as pdf:
        total = len(pdf.pages)
        end = end or total
        with open(output_txt, "w", encoding="utf-8") as f:
            for i in range(max(1, start) - 1, min(end, total)):
                text = pdf.pages[i].extract_text() or ""
                f.write(f"--- Page {i + 1} ---\n")
                f.write(text + "\n")
    print(f"OK: {input_pdf} -> {output_txt} ({end - start + 1} pages)")


if __name__ == "__main__":
    main()
