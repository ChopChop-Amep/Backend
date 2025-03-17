import os
import psycopg

DATABASE_URL = os.getenv("DATABASE_URL", "Database url missing!!")


def get_db_connection():
    conn = psycopg.connect(DATABASE_URL)
    return conn
