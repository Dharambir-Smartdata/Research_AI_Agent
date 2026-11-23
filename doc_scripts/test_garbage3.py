import fitz
import os

input_file = "uploads/20260617_090239_NIST.AI.600-1.pdf"
output_file = "uploads/compressed_merged_medication_record_nist.pdf"

orig_size = os.path.getsize(input_file) / 1024

doc = fitz.open(input_file)

# Let's see what happens if we do garbage=3 without deflating everything or without rebuilding objects
doc.save(output_file, garbage=3, clean=True)
doc.close()

new_size = os.path.getsize(output_file) / 1024
print(f"Compressed size: {new_size:.1f} KB")
