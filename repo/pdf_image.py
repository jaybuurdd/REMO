import fitz
import requests
import random
import string
import os
from services.awsconn import s3

def generate_filename():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

def pdf_to_images(pdf):
    bucketname = "remo-beta-bucket"
    filename = generate_filename()
    response = requests.get(pdf)
    
    # Save the PDF file with the generated filename
    with open(f"{filename}.pdf", 'wb') as f:
        f.write(response.content)
    
    # Open the saved PDF file
    doc = fitz.open(f"{filename}.pdf")
    
    images = []
    for page in doc:
        num = page.number
        pix = page.get_pixmap()
        image_path = f"{filename}-{num}.png"
        pix.save(image_path)
        images.append(image_path)
        
    doc.close()
    os.remove(f"{filename}.pdf")
    
    for image in range(len(images)):
        s3.upload_file(images[image], bucketname, images[image])
        os.remove(images[image])
        images[image] = f"https://{bucketname}.s3.amazonaws.com/{images[image]}"
    
    return [images, filename]