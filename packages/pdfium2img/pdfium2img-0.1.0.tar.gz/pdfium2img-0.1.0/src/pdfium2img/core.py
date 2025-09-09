# SPDX-License-Identifier: Apache-2.0
"""
Core PDF to image conversion functionality using PDFium (pypdfium2).
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

import pypdfium2 as pdfium
from PIL import Image


def _parse_pages(pages_expr: str, n_pages: int) -> List[int]:
    """
    Parse a pages expression like '1,3,5-10' into 0-based page indices.
    Accepts 1-based numbers in the expression for user-friendliness.
    
    Args:
        pages_expr: Page expression string (e.g., "1,3,5-10")
        n_pages: Total number of pages in the document
        
    Returns:
        List of 0-based page indices
        
    Raises:
        ValueError: If page numbers are invalid
    """
    if not pages_expr.strip():
        return list(range(n_pages))
    
    result = set()
    for chunk in pages_expr.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
            
        if "-" in chunk:
            start_s, end_s = chunk.split("-", 1)
            start = int(start_s)
            end = int(end_s)
            if start <= 0 or end <= 0:
                raise ValueError("Pages must be >= 1")
            for p in range(start, end + 1):
                if 1 <= p <= n_pages:
                    result.add(p - 1)
        else:
            p = int(chunk)
            if p <= 0:
                raise ValueError("Pages must be >= 1")
            if 1 <= p <= n_pages:
                result.add(p - 1)
    
    return sorted(result)


def _parse_fill_color(bg: str) -> Tuple[int, int, int, int]:
    """
    Return RGBA tuple from color specification.
    
    Args:
        bg: Color specification ('transparent', 'white', 'black', or '#RRGGBB[AA]')
        
    Returns:
        RGBA tuple (0-255 for each component)
        
    Raises:
        ValueError: If color format is invalid
    """
    named = {
        "transparent": (0, 0, 0, 0),
        "white": (255, 255, 255, 255),
        "black": (0, 0, 0, 255),
    }
    
    bg_lower = bg.lower()
    if bg_lower in named:
        return named[bg_lower]
    
    # Parse hex color
    s = bg.lstrip("#")
    if len(s) == 6:
        r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        return (r, g, b, 255)
    elif len(s) == 8:
        r, g, b, a = (int(s[i:i+2], 16) for i in (0, 2, 4, 6))
        return (r, g, b, a)
    else:
        raise ValueError(f"Invalid color format: {bg}")


def _ensure_ext(fmt: str) -> str:
    """
    Normalize and validate output format.
    
    Args:
        fmt: Format string
        
    Returns:
        Normalized format string
        
    Raises:
        ValueError: If format is not supported
    """
    fmt = fmt.lower()
    if fmt in ("jpg", "jpeg"):
        return "jpg"
    if fmt in ("png", "tiff", "bmp", "webp"):
        return fmt
    raise ValueError(f"Unsupported output format: {fmt}")


def convert_pdf_to_images(
    pdf_path: str | Path,
    output_dir: str | Path = "out_images",
    fmt: str = "png",
    dpi: int = 200,
    pages_expr: str = "",
    password: Optional[str] = None,
    grayscale: bool = False,
    optimize_mode: Optional[str] = None,
    bg: str = "white",
    quality: int = 92,
    draw_annots: bool = True,
    draw_forms: bool = True,
    rotate: int = 0,
) -> List[Path]:
    """
    Convert specified PDF pages to raster images using PDFium (via pypdfium2).
    
    Args:
        pdf_path: Path to input PDF file
        output_dir: Directory to save output images
        fmt: Output format ('png', 'jpg', 'tiff', 'bmp', 'webp')
        dpi: Render DPI (resolution)
        pages_expr: Pages to render (1-based), e.g. "1,3,5-10". Empty = all pages
        password: Password for encrypted PDFs
        grayscale: Convert to grayscale
        optimize_mode: Text rendering optimization ("lcd" or "print")
        bg: Background color ("white", "black", "transparent", or "#RRGGBB[AA]")
        quality: JPEG/WebP quality (1-100)
        draw_annots: Include annotations in output
        draw_forms: Include form fields in output
        rotate: Rotation in degrees (0, 90, 180, 270)
        
    Returns:
        List of output file paths
        
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ValueError: If parameters are invalid
        Exception: If PDF processing fails
        
    Notes:
        - PDFs use 72 points per inch. DPI is converted to scale factor (dpi/72.0)
        - To render forms, pypdfium2 requires init_forms() before accessing pages
        - PDFium is not thread-safe; use multiprocessing for parallel processing
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Validate parameters
    if dpi <= 0:
        raise ValueError("DPI must be positive")
    if not 0 <= quality <= 100:
        raise ValueError("Quality must be between 0 and 100")
    if rotate not in (0, 90, 180, 270):
        raise ValueError("Rotate must be 0, 90, 180, or 270 degrees")
    if optimize_mode is not None and optimize_mode not in ("lcd", "print"):
        raise ValueError("optimize_mode must be 'lcd', 'print', or None")
    
    # Open PDF document
    try:
        pdf = pdfium.PdfDocument(str(pdf_path), password=password)
    except Exception as e:
        raise Exception(f"Failed to open PDF: {e}")
    
    # Initialize form environment before getting pages (required for form rendering)
    if draw_forms:
        pdf.init_forms()
    
    num_pages = len(pdf)
    if num_pages == 0:
        pdf.close()
        raise ValueError("PDF contains no pages")
    
    target_pages = _parse_pages(pages_expr, num_pages)
    if not target_pages:
        pdf.close()
        raise ValueError("No valid pages specified")
    
    # Convert DPI to scale factor (PDF uses 72 points per inch)
    scale = dpi / 72.0
    
    outputs: List[Path] = []
    
    try:
        for i in target_pages:
            page = pdf.get_page(i)
            
            try:
                fill_color = _parse_fill_color(bg)
                
                # Render page to bitmap
                bitmap = page.render(
                    scale=scale,
                    rotation=rotate,
                    may_draw_forms=draw_forms,
                    fill_color=fill_color,
                    grayscale=grayscale,
                    optimize_mode=optimize_mode,
                    draw_annots=draw_annots,
                )
                
                # Convert to PIL Image (zero-copy when possible)
                img = bitmap.to_pil()
                
                # Handle format-specific requirements
                ext = _ensure_ext(fmt)
                if ext in ("jpg", "jpeg", "webp") and img.mode in ("RGBA", "RGBX", "LA"):
                    # JPEG/WebP can't store alpha; convert to RGB
                    img = img.convert("RGB")
                
                # Generate output filename
                out_name = f"{pdf_path.stem}_p{str(i+1).zfill(4)}.{ext}"
                out_path = output_dir / out_name
                
                # Prepare save parameters
                save_params = {}
                if ext in ("jpg", "jpeg", "webp"):
                    save_params["quality"] = quality
                if ext == "png":
                    save_params["optimize"] = True
                
                # Save image
                img.save(out_path, **save_params)
                outputs.append(out_path)
                
                # Clean up page resources
                bitmap.close()
                
            finally:
                page.close()
                
    finally:
        pdf.close()
    
    return outputs
