# -*- coding: utf-8 -*-
"""把 PDF 每页转成 PNG 图片（扫描件 OCR 路径的可选前置步骤）。

⚠️ 这是**可选维护脚本**：会在 <output_dir> 下新建 `page_N.png`（不改源 PDF）。
必须在用户明确要求处理扫描件并确认后运行。

安全边界 / Safety（读 + 写）:
    - **读盘边界**：源 PDF 必须是**真实路径**上的普通文件 —— 路径中任一段是**符号链接
      一律拒绝**（`scripts/pathguard.py` 的 `require_real_file`，fail closed），因此本脚本
      绝不会"跟着链接"读到知识库之外；被拒时报错会回显真实位置，改用真实路径即可。
    - **写盘披露**：运行前打印将写入的目录；只新建 PNG，不删不改其它文件。
    - **写入范围**：<output_dir> 必须位于**源 PDF 所在目录树内**；按真实路径校验
      （解符号链接后仍须在根内，越界即拒绝）
    - 依赖 `pdf2image`（版本见 requirements-optional.txt），并需系统级 poppler；安装前须告知用户并取得确认。

语言 / Language：输出默认中文，**语言可选**（可按用户语言调整文案）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pathguard  # noqa: E402

from pdf2image import convert_from_path  # 可选依赖，版本见 requirements-optional.txt


def resolve_source(pdf_path: str) -> str:
    """源 PDF 必须是**真实路径**上的普通文件；路径中任一段是符号链接即拒绝（fail closed）。"""
    try:
        return pathguard.require_real_file(pdf_path, what="源 PDF")
    except pathguard.PathEscapeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)


def resolve_output_within(pdf_path: str, output_dir: str) -> str:
    """校验输出目录：解析符号链接后，必须落在源 PDF 所在的（真实）目录树内。"""
    root = pathguard.real_root(os.path.dirname(os.path.abspath(os.path.expanduser(pdf_path))))
    resolved = pathguard.real_target(output_dir)
    if not pathguard.is_within(root, resolved, allow_equal=True):
        print(
            f"ERROR: 输出目录必须位于源 PDF 所在目录内（{root}），已拒绝：{output_dir} -> {resolved}",
            file=sys.stderr,
        )
        sys.exit(2)
    return resolved


# Converts each page of a PDF to a PNG image.


def convert(pdf_path, output_dir, max_dim=1000):
    os.makedirs(output_dir, exist_ok=True)
    print(f"[write] 将把每页 PNG 写入：{output_dir}（源 PDF 不改动）")
    images = convert_from_path(pdf_path, dpi=200)

    for i, image in enumerate(images):
        # Scale image if needed to keep width/height under `max_dim`
        width, height = image.size
        if width > max_dim or height > max_dim:
            scale_factor = min(max_dim / width, max_dim / height)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            image = image.resize((new_width, new_height))
        
        image_path = os.path.join(output_dir, f"page_{i+1}.png")
        image.save(image_path)
        print(f"Saved page {i+1} as {image_path} (size: {image.size})")

    print(f"Converted {len(images)} pages to PNG images")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: convert_pdf_to_images.py [input pdf] [output directory]")
        sys.exit(1)
    pdf_path = sys.argv[1]
    source_pdf = resolve_source(pdf_path)
    output_directory = resolve_output_within(source_pdf, sys.argv[2])
    print(f"[read]  源 PDF（真实路径，无符号链接）：{source_pdf}")
    convert(source_pdf, output_directory)
