import fitz # PyMuPDF
import os

doc = fitz.open("uploads/20260617_090239_NIST.AI.600-1.pdf")
print("Page count:", len(doc))

total_text_len = 0
fonts_info = set()
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    total_text_len += len(text)
    for f in page.get_fonts():
        fonts_info.add(f[3]) # font name

print("Total extracted text length:", total_text_len)
print("Unique font names across pages:", fonts_info)
