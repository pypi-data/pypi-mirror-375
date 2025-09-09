# pdfium2img

Convert PDF pages to images using **PDFium** (via [`pypdfium2`](https://pypi.org/project/pypdfium2/)) with **no GPL/AGPL dependencies**. Licensed **Apache-2.0**.

## Why This Package?

Most PDF-to-image libraries in Python (PyMuPDF, pdf2image, ImageMagick/Wand) have GPL/AGPL licenses that can be problematic for commercial use. This package uses PDFium (the same PDF renderer used by Google Chrome) via `pypdfium2`, which is permissively licensed (Apache-2.0 OR BSD-3-Clause).

## Install

```bash
pip install pdfium2img
```

## CLI Usage

```bash
# Basic conversion - all pages to PNG at 200 DPI
pdfium2img input.pdf

# Custom output directory and format
pdfium2img input.pdf -o output_images --format jpg --dpi 300

# Selected pages with transparent background
pdfium2img input.pdf -o out --pages 1,3,5-8 --bg transparent

# High quality JPEG with LCD text optimization
pdfium2img input.pdf --format jpg --dpi 300 --optimize lcd --quality 95

# Grayscale with form fields and annotations
pdfium2img input.pdf --grayscale --forms --annots

# All options
pdfium2img input.pdf \
  -o output_dir \
  --format png \
  --dpi 300 \
  --pages "1,3,5-10" \
  --password "secret" \
  --grayscale \
  --optimize lcd \
  --bg "#ffffff" \
  --quality 92 \
  --forms \
  --annots \
  --rotate 90
```

## Python API Usage

```python
from pdfium2img import convert_pdf_to_images

# Basic usage
output_files = convert_pdf_to_images("input.pdf")

# Advanced usage
output_files = convert_pdf_to_images(
    pdf_path="input.pdf",
    output_dir="output_images",
    fmt="png",                # png, jpg, tiff, bmp, webp
    dpi=300,                  # resolution
    pages_expr="1,3,5-10",    # specific pages (1-based), empty string = all
    password="secret",        # for encrypted PDFs
    grayscale=False,          # convert to grayscale
    optimize_mode="lcd",      # "lcd" or "print" for text rendering
    bg="white",               # "white", "black", "transparent", or "#RRGGBB"
    quality=92,               # JPEG/WebP quality (1-100)
    draw_annots=True,         # include annotations
    draw_forms=True,          # include form fields
    rotate=0                  # rotation in degrees (0, 90, 180, 270)
)

print(f"Generated {len(output_files)} images:")
for file_path in output_files:
    print(f"  {file_path}")
```

## Features

- **Permissive licensing**: No GPL/AGPL dependencies - safe for commercial use
- **High quality**: Uses PDFium (Chrome's PDF renderer) for accurate rendering
- **Fast**: Optimized rendering with configurable DPI and quality settings
- **Flexible**: Support for various output formats (PNG, JPEG, TIFF, BMP, WebP)
- **Complete**: Handles annotations, form fields, transparency, encryption
- **Easy to use**: Simple CLI and Python API

## CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `input` | Input PDF file path | Required |
| `-o, --output-dir` | Output directory | `out_images` |
| `--format` | Output format: png, jpg, tiff, bmp, webp | `png` |
| `--dpi` | Render DPI (resolution) | `200` |
| `--pages` | Pages to render (1-based), e.g. "1,3,5-8" | All pages |
| `--password` | Password for encrypted PDFs | None |
| `--grayscale` | Render in grayscale | False |
| `--optimize` | Text rendering: "lcd" or "print" | None |
| `--bg` | Background color: "white", "black", "transparent", "#RRGGBB" | `white` |
| `--quality` | JPEG/WebP quality (1-100) | `92` |
| `--forms` | Draw form fields | True |
| `--no-forms` | Don't draw form fields | - |
| `--annots` | Draw annotations | True |
| `--no-annots` | Don't draw annotations | - |
| `--rotate` | Rotate output: 0, 90, 180, 270 degrees | `0` |

## Why PDFium is Safe for Commercial Use

- **PDFium**: Apache-2.0 license with patent grant from Google
- **pypdfium2**: Apache-2.0 OR BSD-3-Clause (your choice)
- **Pillow**: MIT-CMU license (permissive)

Unlike GPL/AGPL libraries, these licenses:
- ✅ Allow commercial use without source code disclosure
- ✅ Allow static and dynamic linking
- ✅ Include patent protection
- ✅ Have no "network copyleft" restrictions

## Technical Notes

- **DPI Scaling**: PDFs use 72 points per inch. The package converts DPI to scale factor (dpi/72.0)
- **Form Rendering**: PDFium requires initializing forms before rendering pages with form fields
- **Thread Safety**: PDFium is not thread-safe. Use multiprocessing for parallel processing
- **Memory Efficient**: Uses zero-copy conversion from PDFium bitmaps to PIL images when possible

## Requirements

- Python 3.8+
- pypdfium2 >= 4.30.0
- Pillow >= 9.5.0

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## Contributing

Issues and pull requests welcome! This package aims to be the go-to solution for commercial-friendly PDF to image conversion in Python.
