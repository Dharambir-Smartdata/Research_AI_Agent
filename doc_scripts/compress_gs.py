import os
import subprocess

input_path = "uploads/merged_medication_record_nist.pdf"
output_path = "uploads/compressed_merged_medication_record_nist.pdf"

orig_size = os.path.getsize(input_path)

# Try Ghostscript if available
cmd = [
    "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
    "-dPDFSETTINGS=/screen", "-dNOPAUSE", "-dQUIET", "-dBATCH",
    f"-sOutputFile={output_path}", input_path
]

try:
    subprocess.run(cmd, check=True)
    new_size = os.path.getsize(output_path)
    saved_pct = (1 - new_size / orig_size) * 100
    print(f"Original size: {orig_size / 1024:.1f} KB")
    print(f"New size: {new_size / 1024:.1f} KB")
    print(f"Reduction: {saved_pct:.1f}%")
    print(f"SAVED: {output_path}")
except Exception as e:
    print("Ghostscript failed or not available:", e)
