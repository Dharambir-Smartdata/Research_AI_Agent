import os

pdf_path = "uploads/20260617_090239_NIST.AI.600-1.pdf"

# Combine /screen with -dSubsetFonts=true -dCompressFonts=true -dDownsampleColorImages=true -dDownsampleGrayImages=true -dDownsampleMonoImages=true -dColorImageResolution=72 -dGrayImageResolution=72 -dMonoImageResolution=72
cmd = (f"gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen "
       f"-dSubsetFonts=true -dCompressFonts=true "
       f"-dColorImageResolution=50 -dGrayImageResolution=50 -dMonoImageResolution=50 "
       f"-dNOPAUSE -dQUIET -dBATCH -sOutputFile=uploads/compressed_custom50.pdf {pdf_path}")
os.system(cmd)
print("Custom 50 DPI:", os.path.getsize("uploads/compressed_custom50.pdf")/1024)

cmd = (f"gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen "
       f"-dSubsetFonts=true -dCompressFonts=true "
       f"-dColorImageResolution=30 -dGrayImageResolution=30 -dMonoImageResolution=30 "
       f"-dNOPAUSE -dQUIET -dBATCH -sOutputFile=uploads/compressed_custom30.pdf {pdf_path}")
os.system(cmd)
print("Custom 30 DPI:", os.path.getsize("uploads/compressed_custom30.pdf")/1024)
