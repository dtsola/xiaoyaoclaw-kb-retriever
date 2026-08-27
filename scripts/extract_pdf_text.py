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
"""
import sys

import pdfplumber


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
