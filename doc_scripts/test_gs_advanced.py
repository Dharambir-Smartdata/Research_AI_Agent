import os

pdf_path = "uploads/20260617_090239_NIST.AI.600-1.pdf"

# Try setting font subsetting / embedding flags or color conversions
cmd = f"gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen -dEmbedAllFonts=false -dSubsetFonts=true -dNOPAUSE -dQUIET -dBATCH -sOutputFile=uploads/compressed_no_embed.pdf {pdf_path}"
os.system(cmd)
print("No embed / subset fonts:", os.path.getsize("uploads/compressed_no_embed.pdf")/1024)

# Try monochrome or gray
cmd = f"gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen -sColorConversionStrategy=Gray -dProcessColorModel=/DeviceGray -dNOPAUSE -dQUIET -dBATCH -sOutputFile=uploads/compressed_gray.pdf {pdf_path}"
os.system(cmd)
print("Grayscale screen:", os.path.getsize("uploads/compressed_gray.pdf")/1024)
