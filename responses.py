import os
from dotenv import load_dotenv
# from pdf2image import convert_from_bytes

from repo import review

load_dotenv()
poppler_path = os.getenv('POPPLER_PATH')

def handle_no_file() -> str:
    return "Please attach a PNG file(s) of your resume, to get it reviewed! :)"


async def handle_review(message, files):
    if message.startswith("!review"):
        # review resume image
        image_urls = [attachment.url for attachment in files]
        response = await review.chatgpt_review(image_urls)
        return response