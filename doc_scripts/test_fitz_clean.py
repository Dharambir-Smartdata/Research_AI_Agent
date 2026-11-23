import sys
import fitz
import os

def aggressive_compress(input_path, output_path):
    doc = fitz.open(input_path)
    
    # Iterate through pages and re-render images at very low resolution or remove/replace them
    # But wait, let's see why PyMuPDF increased size: it might have embedded uncompressed fonts or streams.
    # Let's try saving with subset fonts and standard options.
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = "uploads/compressed_merged_medication_record_nist.pdf"
    aggressive_compress(input_file, output_file)
    print(f"SAVED: {output_file}")
    print(f"Size: {os.path.getsize(output_file)/1024:.1f} KB")
