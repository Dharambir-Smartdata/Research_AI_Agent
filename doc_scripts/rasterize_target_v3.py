import os
import fitz

doc = fitz.open("uploads/20260617_090239_NIST.AI.600-1.pdf")
new_doc = fitz.open()

for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=33, colorspace=fitz.csGRAY)
    img_bytes = pix.tobytes("jpeg", jpg_quality=30)
    rect = page.rect
    new_page = new_doc.new_page(width=rect.width, height=rect.height)
    new_page.insert_image(rect, stream=img_bytes)

out_path = "uploads/compressed_target_500kb_v3.pdf"
new_doc.save(out_path, garbage=4, deflate=True)
new_doc.close()

size_kb = os.path.getsize(out_path) / 1024
print(f"SAVED: {out_path}")
print(f"Final Size: {size_kb:.1f} KB")
