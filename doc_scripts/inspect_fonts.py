import fitz

doc = fitz.open("uploads/20260617_090239_NIST.AI.600-1.pdf")
total_objects = len(doc)
print(f"Page count: {len(doc)}")

fonts = set()
for page in doc:
    for f in page.get_fonts():
        fonts.add(f[3]) # font name

print(f"Unique fonts: {len(fonts)}")
for fn in sorted(fonts):
    print(" -", fn)
