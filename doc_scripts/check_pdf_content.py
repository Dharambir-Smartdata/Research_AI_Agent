import fitz
import os

input_file = "uploads/20260617_090239_NIST.AI.600-1.pdf"
output_file = "uploads/compressed_merged_medication_record_nist.pdf"

orig_size = os.path.getsize(input_file) / 1024

doc = fitz.open(input_file)

# Let's inspect what is inside: fonts, images, etc.
for i, page in enumerate(doc):
    il = page.get_images()
    if il:
        print(f"Page {i+1} has {len(il)} images")

doc.close()
