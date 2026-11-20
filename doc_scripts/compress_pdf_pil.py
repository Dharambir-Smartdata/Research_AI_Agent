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
        
        # Open with PIL
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Convert to RGB if necessary
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            
            # Resize / compress using JPEG with quality 30
            output_buffer = io.BytesIO()
            image.save(output_buffer, format="JPEG", quality=30, optimize=True)
            new_image_bytes = output_buffer.getvalue()
            
            doc.update_stream(xref, new_image_bytes)
        except Exception as e:
            print(f"Error processing image xref {xref}: {e}")

doc.save(output_path, garbage=4, deflate=True, clean=True)
doc.close()

new_size = os.path.getsize(output_path)
saved_pct = (1 - new_size / orig_size) * 100

print(f"Original size: {orig_size / 1024:.1f} KB")
print(f"New size: {new_size / 1024:.1f} KB")
print(f"Reduction: {saved_pct:.1f}%")
print(f"SAVED: {output_path}")
