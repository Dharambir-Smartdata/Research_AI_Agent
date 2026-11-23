import os

pdf_path = "uploads/20260617_090239_NIST.AI.600-1.pdf"
orig_size = os.path.getsize(pdf_path)
print(f"Original size: {orig_size} bytes ({orig_size/1024:.1f} KB)")

cmd = f"gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen -dNOPAUSE -dQUIET -dBATCH -sOutputFile=uploads/compressed_screen.pdf {pdf_path}"
print("Running:", cmd)
os.system(cmd)

new_size = os.path.getsize("uploads/compressed_screen.pdf")
print(f"Screen setting size: {new_size} bytes ({new_size/1024:.1f} KB)")
print(f"Savings: {(orig_size - new_size) / orig_size * 100:.2f}%")
