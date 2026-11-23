import fitz

doc = fitz.open("uploads/20260617_090239_NIST.AI.600-1.pdf")
for i, page in enumerate(doc):
    xrefs = page.get_images()
    if xrefs:
        print(f"Page {i+1}: {len(xrefs)} images, xrefs: {xrefs}")
