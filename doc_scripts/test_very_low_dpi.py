import os

pdf_path = "uploads/20260617_090239_NIST.AI.600-1.pdf"

# Let's test varying ImageDownsampleThreshold and ImageResolution in GS
for dpi in [10, 20, 25]:
    out_name = f"uploads/compressed_dpi{dpi}.pdf"
    cmd = (f"gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen "
           f"-dColorImageDownsampleType=/Average -dColorImageResolution={dpi} "
           f"-dGrayImageDownsampleType=/Average -dGrayImageResolution={dpi} "
           f"-dMonoImageDownsampleType=/Average -dMonoImageResolution={dpi} "
           f"-dNOPAUSE -dQUIET -dBATCH -sOutputFile={out_name} {pdf_path}")
    os.system(cmd)
    size_kb = os.path.getsize(out_name) / 1024
    print(f"DPI {dpi}: {size_kb:.1f} KB")
