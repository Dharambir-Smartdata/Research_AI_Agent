import os
import subprocess

input_path = "uploads/merged_medication_record_nist.pdf"
output_path = "uploads/compressed_merged_medication_record_nist.pdf"

orig_size = os.path.getsize(input_path)

cmd = [
    "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
    "-dPDFSETTINGS=/screen",
    "-dDownscaleFactor=2",
    "-dNOPAUSE", "-dQUIET", "-dBATCH",
    f"-sOutputFile={output_path}", input_path
]

subprocess.run(cmd, check=True)
new_size = os.path.getsize(output_path)
saved_pct = (1 - new_size / orig_size) * 100
print(f"Original size: {orig_size / 1024:.1f} KB")
print(f"New size: {new_size / 1024:.1f} KB")
print(f"Reduction: {saved_pct:.1f}%")
print(f"SAVED: {output_path}")
