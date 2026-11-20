import os
import fitz

input_path = "uploads/merged_medication_record_nist.pdf"
output_path = "uploads/compressed_merged_medication_record_nist.pdf"

orig_size = os.path.getsize(input_path)

doc = fitz.open(input_path)

# Extract embedded images and downscale them
for i, page in enumerate(doc):
    image_list = page.get_images(full=True)
    for img_index, img in enumerate(image_list):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]
        
        # If image is large, re-encode with lower quality
        if len(image_bytes) > 50000:
            pix = fitz.Pixmap(doc, xref)
            if pix.n > 3:
                pix = fitz.Pixmap(fitz.csRGB, pix)
            # scale down
            pix = fitz.Pixmap(pix, 0.5, 0.5)
            new_bytes = pix.tobytes("jpeg", jpg_quality=50)
            doc.update_stream(xref, new_bytes)

doc.save(output_path, garbage=4, deflate=True, clean=True)
doc.close()

new_size = os.path.getsize(output_path)
saved_pct = (1 - new_size / orig_size) * 100

print(f"Original size: {orig_size / 1024:.1f} KB")
print(f"New size: {new_size / 1024:.1f} KB")
print(f"Reduction: {saved_pct:.1f}%")
print(f"SAVED: {output_path}")
