# SPDX-License-Identifier: Apache-2.0
"""
pdfium2img: Convert PDF pages to images using PDFium (pypdfium2) — no GPL/AGPL deps.

This package provides a commercial-friendly solution for converting PDF pages to images
using PDFium (the same PDF renderer used by Google Chrome) via the pypdfium2 library.
All dependencies are permissively licensed (Apache-2.0, BSD-3-Clause, MIT).

Example usage:
    from pdfium2img import convert_pdf_to_images
    
    # Convert all pages to PNG at 300 DPI
    output_files = convert_pdf_to_images("document.pdf", dpi=300)
    
    # Convert specific pages to JPEG with custom settings
    output_files = convert_pdf_to_images(
        pdf_path="document.pdf",
        output_dir="images",
        fmt="jpg",
        pages_expr="1,3,5-10",
        quality=95
    )
"""

from .core import convert_pdf_to_images

__version__ = "0.1.0"
__author__ = "Abhishake"
__email__ = "admin@gyaan.gg"
__license__ = "Apache-2.0"

__all__ = ["convert_pdf_to_images"]
