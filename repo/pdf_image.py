import fitz

def pdf_to_images(pdf): 
    doc = fitz.open(pdf)
    images = []
    for page in doc:
        num = page.number
        pix = page.get_pixmap()
        pix.save(f"page-{num}.png")
        images.append(pix)
    
    return images