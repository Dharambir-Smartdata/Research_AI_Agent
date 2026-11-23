import fitz

doc = fitz.open("uploads/20260617_090239_NIST.AI.600-1.pdf")
for page_num in [0, 1, 3]: # 0-indexed for pages 1, 2, 4
    page = doc[page_num]
    print(f"--- Page {page_num+1} ---")
    for img in page.get_images(full=True):
        xref = img[0]
        base_image = doc.extract_image(xref)
        print(f"  xref {xref}: {base_image['ext']}, {base_image['width']}x{base_image['height']}, {len(base_image['image'])/1024:.1f} KB")
