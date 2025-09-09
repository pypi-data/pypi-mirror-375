# SPDX-License-Identifier: Apache-2.0
"""
Command-line interface for pdfium2img.
"""
import argparse
import sys
from pathlib import Path

from .core import convert_pdf_to_images


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="pdfium2img",
        description="Convert PDF pages to images (no GPL/AGPL deps). Uses PDFium via pypdfium2.",
        epilog="Examples:\n"
               "  pdfium2img input.pdf\n"
               "  pdfium2img input.pdf -o output --format jpg --dpi 300\n"
               "  pdfium2img input.pdf --pages 1,3,5-8 --bg transparent\n"
               "  pdfium2img input.pdf --grayscale --optimize lcd --quality 95",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Required arguments
    parser.add_argument(
        "input", 
        help="Input PDF file path"
    )
    
    # Output options
    parser.add_argument(
        "-o", "--output-dir", 
        default="out_images", 
        help="Output directory (default: out_images)"
    )
    parser.add_argument(
        "--format", 
        default="png", 
        choices=["png", "jpg", "jpeg", "tiff", "bmp", "webp"],
        help="Image format (default: png)"
    )
    
    # Rendering options
    parser.add_argument(
        "--dpi", 
        type=int, 
        default=200, 
        help="Render DPI/resolution (default: 200)"
    )
    parser.add_argument(
        "--pages", 
        default="", 
        help="Pages to render, e.g. '1,3,5-8' (1-based). Default: all pages"
    )
    parser.add_argument(
        "--password", 
        default=None, 
        help="Password for encrypted PDFs"
    )
    
    # Visual options
    parser.add_argument(
        "--grayscale", 
        action="store_true", 
        help="Render in grayscale"
    )
    parser.add_argument(
        "--optimize", 
        choices=["lcd", "print"], 
        default=None,
        help="PDFium optimize mode: 'lcd' for subpixel text, 'print' for print-like rendering"
    )
    parser.add_argument(
        "--bg", 
        default="white",
        help="Background color: 'transparent', 'white', 'black', or #RRGGBB[AA] (default: white)"
    )
    parser.add_argument(
        "--quality", 
        type=int, 
        default=92, 
        help="Quality for JPEG/WebP, 1-100 (default: 92)"
    )
    parser.add_argument(
        "--rotate", 
        type=int, 
        choices=[0, 90, 180, 270], 
        default=0, 
        help="Rotate output in degrees (default: 0)"
    )
    
    # Content options
    parser.add_argument(
        "--annots", 
        dest="draw_annots", 
        action="store_true", 
        help="Draw annotations (default: enabled)"
    )
    parser.add_argument(
        "--no-annots", 
        dest="draw_annots", 
        action="store_false", 
        help="Do not draw annotations"
    )
    parser.add_argument(
        "--forms", 
        dest="draw_forms", 
        action="store_true", 
        help="Draw form fields (default: enabled)"
    )
    parser.add_argument(
        "--no-forms", 
        dest="draw_forms", 
        action="store_false", 
        help="Do not draw form fields"
    )
    
    # Set defaults for boolean flags
    parser.set_defaults(draw_annots=True, draw_forms=True)
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(2)
    
    if not input_path.is_file():
        print(f"Error: Input path is not a file: {input_path}", file=sys.stderr)
        sys.exit(2)
    
    # Validate quality parameter
    if not 1 <= args.quality <= 100:
        print(f"Error: Quality must be between 1 and 100, got {args.quality}", file=sys.stderr)
        sys.exit(2)
    
    # Validate DPI parameter
    if args.dpi <= 0:
        print(f"Error: DPI must be positive, got {args.dpi}", file=sys.stderr)
        sys.exit(2)
    
    try:
        output_files = convert_pdf_to_images(
            pdf_path=input_path,
            output_dir=Path(args.output_dir),
            fmt=args.format,
            dpi=args.dpi,
            pages_expr=args.pages,
            password=args.password,
            grayscale=args.grayscale,
            optimize_mode=args.optimize,
            bg=args.bg,
            quality=args.quality,
            draw_annots=args.draw_annots,
            draw_forms=args.draw_forms,
            rotate=args.rotate,
        )
        
        print(f"Successfully converted {len(output_files)} pages:")
        for output_file in output_files:
            print(f"  {output_file}")
            
    except KeyboardInterrupt:
        print("\nConversion interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
