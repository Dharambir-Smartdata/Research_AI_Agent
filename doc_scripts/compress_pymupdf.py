import fitz

doc = fitz.open("uploads/20260617_090239_NIST.AI.600-1.pdf")
doc.save("uploads/compressed_pymupdf_garbage.pdf", garbage=4, deflate=True, clean=True)

import os
size = os.path.getsize("uploads/compressed_pymupdf_garbage.pdf")
print(f"SAVED: uploads/compressed_pymupdf_garbage.pdf")
print(f"Size: {size / 1024:.1f} KB")
