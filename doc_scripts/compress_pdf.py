"""
Compress a PDF file using Ghostscript and PyMuPDF optimization.
Usage: python compress_pdf.py <input_pdf> [output_pdf]
"""
import sys
import os
import shutil
import subprocess
from pathlib import Path
import fitz


def compress_pdf(input_path: str, output_path: str = None) -> str:
    inp = Path(input_path)
    if not inp.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if not output_path:
        output_path = inp.parent / f"compressed_{inp.name}"
    else:
        output_path = Path(output_path)

    orig_size = inp.stat().st_size
    temp_output = output_path.parent / f"temp_{output_path.name}"

    compressed = False
    # Try Ghostscript first if available for high compression
    if shutil.which("gs"):
        for setting in ["/ebook", "/screen"]:
            try:
                cmd = [
                    "gs",
                    "-sDEVICE=pdfwrite",
                    "-dCompatibilityLevel=1.4",
                    f"-dPDFSETTINGS={setting}",
                    "-dNOPAUSE",
                    "-dQUIET",
                    "-dBATCH",
                    f"-sOutputFile={temp_output}",
                    str(inp),
                ]
                subprocess.run(cmd, check=True, timeout=30)
                if temp_output.exists() and temp_output.stat().st_size < orig_size:
                    shutil.move(str(temp_output), str(output_path))
                    compressed = True
                    break
            except Exception:
                pass
            finally:
                if temp_output.exists():
                    temp_output.unlink(missing_ok=True)

    if not compressed:
        doc = fitz.open(str(inp))
        doc.save(str(output_path), garbage=4, deflate=True, clean=True)
        doc.close()

    new_size = output_path.stat().st_size
    orig_kb = orig_size / 1024
    new_kb = new_size / 1024
    reduction = ((orig_size - new_size) / orig_size * 100) if orig_size else 0
    print(f"Original size: {orig_kb:.1f} KB")
    print(f"Compressed size: {new_kb:.1f} KB")
    print(f"Reduction: {reduction:.1f}%")
    print(f"SAVED: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python compress_pdf.py <input_pdf> [output_pdf]")
        sys.exit(1)
    in_file = sys.argv[1]
    out_file = sys.argv[2] if len(sys.argv) > 2 else None
    compress_pdf(in_file, out_file)
