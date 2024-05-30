import os
from dotenv import load_dotenv

from repo.review import chatgpt_review
from services.logging import logger

load_dotenv()
poppler_path = os.getenv('POPPLER_PATH')

async def handle_review(message, files):
    if message.startswith("!review"):
        urls = files
        try:
            if files[0].url:
                urls = [attachment.url for attachment in files]
        except AttributeError:
            logger.info("Files do not have 'url' attribute, using the provided list as is.")
        return await chatgpt_review(urls)
