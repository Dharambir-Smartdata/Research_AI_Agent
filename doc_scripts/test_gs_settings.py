import os

pdf_path = "uploads/20260617_090239_NIST.AI.600-1.pdf"

# Let's test various gs settings
settings = ["/screen", "/ebook", "/printer", "/prepress"]
for s in settings:
    out = f"uploads/compressed_{s.strip('/')}.pdf"
    cmd = f"gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS={s} -dNOPAUSE -dQUIET -dBATCH -sOutputFile={out} {pdf_path}"
    os.system(cmd)
    sz = os.path.getsize(out)
    print(f"Setting {s}: {sz/1024:.1f} KB")
