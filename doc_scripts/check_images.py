import os
import fitz

input_path = "uploads/merged_medication_record_nist.pdf"
output_path = "uploads/compressed_merged_medication_record_nist.pdf"

orig_size = os.path.getsize(input_path)

doc = fitz.open(input_path)
for page in doc:
    il = page.get_images()
    for img in il:
        xref = img[0]
        # remove or replace image if needed, or let's check what images exist
print("Images count:", sum(len(p.get_images()) for p in doc))
doc.close()
