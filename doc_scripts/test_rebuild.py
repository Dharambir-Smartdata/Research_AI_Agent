import os
import fitz

input_path = "uploads/merged_medication_record_nist.pdf"
output_path = "uploads/compressed_merged_medication_record_nist.pdf"

orig_size = os.path.getsize(input_path)

doc = fitz.open(input_path)

for page in doc:
    pix = page.get_pixmap(dpi=110)
    img_bytes = pix.tobytes("jpeg", jpg_quality=55)
    
    # Replace page content with single compressed image
    rect = page.rect
    page.clean_contents()
    # Remove existing drawings/images by clearing content and inserting image
    # Actually, simpler: render page to image and build new doc
    
doc.close()
