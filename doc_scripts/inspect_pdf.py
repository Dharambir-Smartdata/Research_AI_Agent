import os
import fitz

input_path = "uploads/merged_medication_record_nist.pdf"
output_path = "uploads/compressed_merged_medication_record_nist.pdf"

orig_size = os.path.getsize(input_path)

doc = fitz.open(input_path)
print("Page count:", len(doc))
for i, page in enumerate(doc):
    text = page.get_text()
    print(f"Page {i+1} text length: {len(text)}, images: {len(page.get_images())}")
doc.close()
