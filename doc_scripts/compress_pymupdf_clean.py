import sys
import fitz # PyMuPDF

def compress_pdf(input_path, output_path):
    doc = fitz.open(input_path)
    
    # Set clean metadata and remove unnecessary streams if possible
    # We can save with garbage collection (4), deflate (1), and cleaning
    doc.save(output_path, garbage=4, deflate=True, deflate_images=True, deflate_fonts=True)
    doc.close()

if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "uploads/20260617_090239_NIST.AI.600-1.pdf"
    output_file = "uploads/compressed_merged_medication_record_nist.pdf"
    
    import os
    orig_size = os.path.getsize(input_file) / 1024
    compress_pdf(input_file, output_file)
    new_size = os.path.getsize(output_file) / 1024
    
    print(f"Original size: {orig_size:.1f} KB")
    print(f"New size: {new_size:.1f} KB")
    print(f"Reduction: {100 * (1 - new_size/orig_size):.1f}%")
    print(f"SAVED: {output_file}")
