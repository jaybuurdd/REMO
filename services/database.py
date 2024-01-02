import os
import psycopg2
from dotenv import load_dotenv

from services.logging import logger


load_dotenv()

def config_rds_db():
    logger.info("DB Config Started...")
    global rds
    print(os.getenv('AWS_POSTGRES_DB_NAME'))
    print(os.getenv('AWS_POSTGRES_MASTER_USERNAME'))
    print(os.getenv('AWS_POSTGRES_MASTER_PASSWORD'))
    print(os.getenv('AWS_POSTGRES_HOST'))

    # connect to RDS db
    conn = psycopg2.connect(
        dbname=os.getenv('AWS_POSTGRES_DB_NAME'),
        user=os.getenv('AWS_POSTGRES_MASTER_USERNAME'),
        password=os.getenv('AWS_POSTGRES_MASTER_PASSWORD'),
        host=os.getenv('AWS_POSTGRES_HOST'),
        port="5432",
        sslmode="require"
    )

    cursor = conn.cursor()
    logger.info("DB Config Ended...")
    
    return cursor

