import fitz
import os

input_file = "uploads/20260617_090239_NIST.AI.600-1.pdf"
output_file = "uploads/compressed_merged_medication_record_nist.pdf"

orig_size = os.path.getsize(input_file) / 1024

doc = fitz.open(input_file)

# Save with garbage collection, deflate, and incremental/clean options
doc.save(output_file, garbage=4, deflate=True, deflate_images=True, deflate_fonts=True)
doc.close()

new_size = os.path.getsize(output_file) / 1024
print(f"Original size: {orig_size:.1f} KB")
print(f"Compressed size: {new_size:.1f} KB")
print(f"Saved: {100 * (1 - new_size/orig_size):.1f}%")
print(f"SAVED: {output_file}")
