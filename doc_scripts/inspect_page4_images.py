import fitz

doc = fitz.open("uploads/20260617_090239_NIST.AI.600-1.pdf")
page = doc[3] # 0-indexed page 4
for img in page.get_images():
    xref = img[0]
    base_image = doc.extract_image(xref)
    print(f"XREF {xref}: {base_image['width']}x{base_image['height']}, {base_image['ext']}, {len(base_image['image'])} bytes")
