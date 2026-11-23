import fitz

doc = fitz.open("uploads/20260617_090239_NIST.AI.600-1.pdf")
for i, page in enumerate(doc):
    il = page.get_images()
    if il:
        print(f"Page {i+1}: {len(il)} images")
