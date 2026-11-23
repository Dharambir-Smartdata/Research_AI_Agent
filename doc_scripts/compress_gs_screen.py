import subprocess
import os

input_file = "uploads/20260617_090239_NIST.AI.600-1.pdf"
output_file = "uploads/compressed_merged_medication_record_nist.pdf"

orig_size = os.path.getsize(input_file) / 1024

cmd = [
    "gs",
    "-sDEVICE=pdfwrite",
    "-dCompatibilityLevel=1.4",
    "-dPDFSETTINGS=/screen",
    "-dNOPAUSE",
    "-dQUIET",
    "-dBATCH",
    f"-sOutputFile={output_file}",
    input_file
]

subprocess.run(cmd, check=True)
new_size = os.path.getsize(output_file) / 1024
print(f"Original size: {orig_size:.1f} KB")
print(f"Compressed size: {new_size:.1f} KB")
print(f"Saved: {100 * (1 - new_size/orig_size):.1f}%")
print(f"SAVED: {output_file}")
