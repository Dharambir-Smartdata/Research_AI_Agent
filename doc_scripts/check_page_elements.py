import fitz

doc = fitz.open("uploads/20260617_090239_NIST.AI.600-1.pdf")
for i, page in enumerate(doc):
    text_len = len(page.get_text())
    imgs = page.get_images(full=True)
    if imgs or text_len < 100:
        print(f"Page {i+1}: text len={text_len}, images={len(imgs)}")
