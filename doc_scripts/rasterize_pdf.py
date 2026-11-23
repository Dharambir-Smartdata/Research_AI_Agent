import os
import fitz

doc = fitz.open("uploads/20260617_090239_NIST.AI.600-1.pdf")
print(f"Original pages: {len(doc)}")

# Render each page to an image and compile into a new PDF
new_doc = fitz.open()
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=72)
    img_bytes = pix.tobytes("jpeg", jpg_quality=60)
    
    # Create a new page with the same dimensions
    rect = page.rect
    new_page = new_doc.new_page(width=rect.width, height=rect.height)
    new_page.insert_image(rect, stream=img_bytes)

out_path = "uploads/rasterized_72dpi.pdf"
new_doc.save(out_path, garbage=4, deflate=True)
new_doc.close()

print(f"Rasterized 72 DPI size: {os.path.getsize(out_path)/1024:.1f} KB")

# Test 50 DPI
new_doc = fitz.open()
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=50)
    img_bytes = pix.tobytes("jpeg", jpg_quality=50)
    rect = page.rect
    new_page = new_doc.new_page(width=rect.width, height=rect.height)
    new_page.insert_image(rect, stream=img_bytes)

out_path_50 = "uploads/rasterized_50dpi.pdf"
new_doc.save(out_path_50, garbage=4, deflate=True)
new_doc.close()

print(f"Rasterized 50 DPI size: {os.path.getsize(out_path_50)/1024:.1f} KB")

# Test 40 DPI
new_doc = fitz.open()
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=40)
    img_bytes = pix.tobytes("jpeg", jpg_quality=45)
    rect = page.rect
    new_page = new_doc.new_page(width=rect.width, height=rect.height)
    new_page.insert_image(rect, stream=img_bytes)

out_path_40 = "uploads/rasterized_40dpi.pdf"
new_doc.save(out_path_40, garbage=4, deflate=True)
new_doc.close()

print(f"Rasterized 40 DPI size: {os.path.getsize(out_path_40)/1024:.1f} KB")
