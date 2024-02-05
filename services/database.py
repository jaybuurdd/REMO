import os
import psycopg2
from dotenv import load_dotenv

from services.logging import logger

load_dotenv()

def get_rds_instance():
    # Fetch environment variables
    db_name = os.getenv('AWS_POSTGRES_DEV_DB_NAME')
    db_user = os.getenv('AWS_POSTGRES_DEV_MASTER_USERNAME')
    db_password = os.getenv('AWS_POSTGRES_DEV_MASTER_PASSWORD')
    db_host = os.getenv('AWS_DEV_POSTGRES_HOST')

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

    return  conn, cursor

