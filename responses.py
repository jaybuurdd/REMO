import os
import io
import pytesseract
from dotenv import load_dotenv
# from pdf2image import convert_from_bytes

from repo import review

load_dotenv()
poppler_path = os.getenv('POPPLER_PATH')

def handle_no_file() -> str:
    return "Please attach a PNG file(s) of your resume, to get it reviewed! :)"


async def handle_review(message, files):
    if message == "!review":
        # Check if all files are PNGs
        if all(f.filename.lower().endswith('.png') for f in files):
            image_urls = [attachment.url for attachment in files]
            return review.chatgpt_review(image_urls)
        else:
            # Return a message if any file is not a PNG
            return "Sorry, I only accept PNG files. Please try again."

        

# def extract_pdf_stream(stream):
#     try:
#         print(f"poppler path: {poppler_path}")
#         images = convert_from_bytes(stream.read(), poppler_path=poppler_path)
#         text = " ".join([pytesseract.image_to_string(image) for image in images])
#         return text
#     except Exception as e:
#         print(f"Error processing PDF with Tesseract: {e}")
#         return