import boto3
from dotenv import load_dotenv
import os

load_dotenv()

# Create a session using your AWS credentials
session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
)

s3 = session.client('s3')