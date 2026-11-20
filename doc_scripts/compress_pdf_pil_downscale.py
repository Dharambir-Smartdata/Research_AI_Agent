import os
import fitz
from PIL import Image
import io

input_path = "uploads/merged_medication_record_nist.pdf"
output_path = "uploads/compressed_merged_medication_record_nist.pdf"

orig_size = os.path.getsize(input_path)

doc = fitz.open(input_path)

for page in doc:
    image_list = page.get_images(full=True)
    for img in image_list:
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        
        try:
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            
            # Downscale image dimensions by half
            w, h = image.size
            image = image.resize((max(1, w // 2), max(1, h // 2)), Image.Resampling.LANCZOS)
            
            output_buffer = io.BytesIO()
            image.save(output_buffer, format="JPEG", quality=40, optimize=True)
            new_image_bytes = output_buffer.getvalue()
            
            doc.update_stream(xref, new_image_bytes)
        except Exception as e:
            pass

doc.save(output_path, garbage=4, deflate=True, clean=True)
doc.close()

new_size = os.path.getsize(output_path)
saved_pct = (1 - new_size / orig_size) * 100

print(f"Original size: {orig_size / 1024:.1f} KB")
print(f"New size: {new_size / 1024:.1f} KB")
print(f"Reduction: {saved_pct:.1f}%")
print(f"SAVED: {output_path}")
