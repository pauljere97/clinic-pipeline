from dotenv import load_dotenv
import psycopg2
import os
load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")

db_connection = psycopg2.connect(
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    database=POSTGRES_DB
)

db_connection.autocommit = True # Set autocommit to True to avoid the need for explicit commit statements

with db_connection.cursor() as cursor:
    cursor.execute("SELECT 1")
    if cursor.fetchone() == (1,):
        print(f"==> Database connection successful at {POSTGRES_HOST}:{POSTGRES_PORT}")
    else:
        print(f"==> Database connection failed at {POSTGRES_HOST}:{POSTGRES_PORT}")

