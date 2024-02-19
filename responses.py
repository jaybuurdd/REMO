import os
from dotenv import load_dotenv

from repo.review import chatgpt_review

load_dotenv()
poppler_path = os.getenv('POPPLER_PATH')

async def handle_review(message, files):
    if message.startswith("!review"):
        # review resume image
        if hasattr(files, 'url'):
            image_urls = [attachment.url for attachment in files]
            response = await chatgpt_review(image_urls)
        else:
            print(f"files: {files}")
            response = await chatgpt_review(files)

        return response