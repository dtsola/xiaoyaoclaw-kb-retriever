# PDF 读取与分析（OpenClaw 版 · 双平台统一 Python 路线）

> ⚠️ **使用本文档前请注意**：本文档应在实际处理 PDF 文件之前完整阅读，以选择最合适的工具和方法。不要在未阅读本文档的情况下盲目尝试处理 PDF。

用于从 PDF 文件中提取文本、表格和元数据的方法。

## 平台策略（重要）

**PDF 处理统一走 Python 路线**（pdfplumber + pypdf + pypdfium2），Windows 与 macOS 行为完全一致：
- 双平台统一安装：`pip install pdfplumber pypdf pypdfium2`
- ⚠️ 安装前先告知用户「将安装这些包（会修改 Python 环境）」，获确认后再执行（详见 SKILL.md「依赖自安装」）
- 不依赖 poppler/pdftotext 二进制（Windows/macOS 默认都没有，安装路径还不同——避免双平台差异）
- 若系统中恰好已有 `pdftotext`（可选加速），可优先使用；但**默认路径是 Python，且必须输出到文件而非 stdout**

## 快速决策表

| 场景 | 推荐工具 | 原因 | 代码示例 |
|------|----------|------|---------|
| 纯文本提取（最常见） | pdfplumber | 双平台统一，提取质量好 | `page.extract_text()` |
| 需要提取表格 | pdfplumber | 表格识别能力强 | `page.extract_tables()` |
| 需要元数据 | pypdf | 轻量级 | `reader.metadata` |
| 扫描PDF（图片） | pypdfium2 转图片 + OCR | 无其他选择 | `page.render()` |
| 加密 PDF | pypdf | 支持解密 | `reader.decrypt()` |

## 文本提取优先级

**推荐优先级（从高到低）**：
1. **pdfplumber**（双平台统一，文本+表格都强，首选）
2. pypdf（轻量级，简单提取/元数据）
3. pdftotext 命令行（**仅当系统已安装**，可选加速）
4. OCR（仅用于扫描PDF或无法直接提取文本的情况）

## 快速开始：pdfplumber 提取文本（推荐，双平台通用）

> ⚠️ **重要**：必须将提取结果保存到文件，不要直接打印到 stdout，否则会占用大量 token！

将以下脚本保存为 `scripts/extract_pdf_text.py`（本项目已提供），双平台通用：

```python
# scripts/extract_pdf_text.py — 双平台通用 PDF 文本提取
# 用法: python extract_pdf_text.py input.pdf output.txt [start_page] [end_page]
import sys
import pdfplumber

def main():
    if len(sys.argv) < 3:
        print("用法: python extract_pdf_text.py <input.pdf> <output.txt> [start_page] [end_page]", file=sys.stderr)
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
```

**使用流程**：
1. `python scripts/extract_pdf_text.py input.pdf output.txt`（提取到临时文件，不占 token）
2. 用 exec（Select-String / grep）对生成的文本文件检索关键词
3. 只读取匹配部分的上下文，而非全文

**提取特定页面**（大 PDF 用，减少处理量）：
- Windows/macOS 通用：`python scripts/extract_pdf_text.py input.pdf output.txt 1 5`（第 1-5 页）

## Python 库

### pypdf - 基本文本提取与元数据

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")

# 提取全部文本
for page in reader.pages:
    text = page.extract_text()

# 提取元数据
meta = reader.metadata
print(f"Title: {meta.title}")
print(f"Author: {meta.author}")
```

### pdfplumber - 文本和表格提取（首选）

#### 提取文本

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
```

#### 提取表格

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"Table {j+1} on page {i+1}:")
            for row in table:
                print(row)
```

#### 高级表格提取（转为 DataFrame）

```python
import pandas as pd
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        for table in page.extract_tables():
            if table:  # 检查表格非空
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

if all_tables:
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```

#### 复杂表格的高级设置

```python
import pdfplumber

with pdfplumber.open("complex_table.pdf") as pdf:
    page = pdf.pages[0]
    table_settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "snap_tolerance": 3,
        "intersection_tolerance": 15
    }
    tables = page.extract_tables(table_settings)
```

### pypdfium2 - 快速渲染（扫描件转图片）

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("document.pdf")

# 渲染单页为图片（供 OCR 或人工查看）
page = pdf[0]
bitmap = page.render(scale=2.0)
img = bitmap.to_pil()
img.save("page_1.png", "PNG")

# 渲染多页
for i, page in enumerate(pdf):
    bitmap = page.render(scale=1.5)
    img = bitmap.to_pil()
    img.save(f"page_{i+1}.jpg", "JPEG", quality=90)
```

## OCR 提取（扫描PDF）

> 需要：`pip install pytesseract pdf2image`（双平台通用；macOS 需 `brew install tesseract`，Windows 需安装 Tesseract OCR 并加入 PATH——仅扫描件场景才需要）

```python
import pytesseract
from pdf2image import convert_from_path

# PDF 转图片
images = convert_from_path('scanned.pdf')

# OCR 每一页
text = ""
for i, image in enumerate(images):
    text += f"Page {i+1}:\n"
    text += pytesseract.image_to_string(image)
    text += "\n\n"
```

> ⚠️ OCR 依赖较重（tesseract 二进制），仅在扫描件（无文本层）时启用；常规 PDF 走 pdfplumber 即可。

## 处理加密 PDF

```python
from pypdf import PdfReader

reader = PdfReader("encrypted.pdf")
if reader.is_encrypted:
    reader.decrypt("password")

for page in reader.pages:
    text = page.extract_text()
```

## 批量处理

```python
import os, glob
from pypdf import PdfReader
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def batch_extract_text(input_dir):
    """批量提取文本（双平台通用）"""
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    for pdf_file in pdf_files:
        try:
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            output_file = pdf_file.replace('.pdf', '.txt')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            logger.info(f"Extracted: {pdf_file}")
        except Exception as e:
            logger.error(f"Failed {pdf_file}: {e}")
            continue
```

## 性能优化

1. **文件输出优先**：始终将提取结果保存到文件，然后用 exec 搜索 / read 局部读取，避免占用大量 token
2. **大型PDF**：用 `extract_pdf_text.py` 的 start_page/end_page 参数按页范围提取，避免处理整个文件
3. **文本提取**：pdfplumber 首选；表格用 `extract_tables()`；元数据用 pypdf
4. **内存管理**：逐页或分块处理大文件

## 快速参考

| 任务 | 最佳工具 | 代码 |
|------|----------|------|
| 提取文本 | pdfplumber | `page.extract_text()` |
| 提取表格 | pdfplumber | `page.extract_tables()` |
| 元数据 | pypdf | `reader.metadata` |
| OCR 扫描PDF | pytesseract + pypdfium2 | 先转图片再OCR |
| PDF转图片 | pypdfium2 | `page.render()` |

## 可用包（双平台 pip 安装）

- **pdfplumber** - 文本和表格提取（MIT 许可）⭐ 首选
- **pypdf** - 基本操作 / 元数据 / 加密（BSD 许可）
- **pypdfium2** - 快速渲染转图片（Apache/BSD 许可）
- **pytesseract + pdf2image** - OCR（Apache 许可，仅扫描件）
