import os
import fitz

input_path = "uploads/merged_medication_record_nist.pdf"
output_path = "uploads/compressed_merged_medication_record_nist.pdf"

orig_size = os.path.getsize(input_path)

doc = fitz.open(input_path)
new_doc = fitz.open()

for page in doc:
    pix = page.get_pixmap(dpi=110)
    img_bytes = pix.tobytes("jpeg", jpg_quality=60)
    
    new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
    new_page.insert_image(new_page.rect, stream=img_bytes)

new_doc.save(output_path, garbage=4, deflate=True)
doc.close()
new_doc.close()

new_size = os.path.getsize(output_path)
saved_pct = (1 - new_size / orig_size) * 100

print(f"Original size: {orig_size / 1024:.1f} KB")
print(f"New size: {new_size / 1024:.1f} KB")
print(f"Reduction: {saved_pct:.1f}%")
print(f"SAVED: {output_path}")
