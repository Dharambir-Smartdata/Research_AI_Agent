import os

pdf_path = "uploads/20260617_090239_NIST.AI.600-1.pdf"

# Try different Postscript/Ghostscript distillation options to strip unused objects and flatten
cmd = (f"gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen "
       f"-dDetectDuplicateImages=true -dFastWebView=false "
       f"-dNOPAUSE -dQUIET -dBATCH -sOutputFile=uploads/compressed_clean.pdf {pdf_path}")
os.system(cmd)
print("Clean option size:", os.path.getsize("uploads/compressed_clean.pdf")/1024)

# Try removing metadata and thumbnails
cmd = (f"gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen "
       f"-dNoOutputFonts -dNOPAUSE -dQUIET -dBATCH -sOutputFile=uploads/compressed_no_fonts.pdf {pdf_path}")
os.system(cmd)
print("No fonts output size:", os.path.getsize("uploads/compressed_no_fonts.pdf")/1024)
