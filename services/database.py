import os
#import redis
import psycopg2
from dotenv import load_dotenv

from services.logging import logger

load_dotenv()

def get_rds_instance():
    logger.info("Starting database connection configuration...")
    # Fetch environment variables
    db_name = os.getenv('AWS_POSTGRES_DB_NAME')
    db_user = os.getenv('AWS_POSTGRES_MASTER_USERNAME')
    db_password = os.getenv('AWS_POSTGRES_MASTER_PASSWORD')
    db_host = os.getenv('AWS_POSTGRES_HOST')
    
    # connect to RDS db
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port="5432",
        sslmode="require"
    )

    cursor = conn.cursor()
    logger.info("Database connection successful...")

    return  conn, cursor


