import fitz

doc = fitz.open("uploads/20260617_090239_NIST.AI.600-1.pdf")
image_count = 0
total_img_bytes = 0

for i, page in enumerate(doc):
    image_list = page.get_images(full=True)
    for img in image_list:
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        total_img_bytes += len(image_bytes)
        image_count += 1

print(f"Total images found: {image_count}")
print(f"Total size of embedded images: {total_img_bytes / 1024:.1f} KB")
