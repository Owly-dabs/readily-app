# db.py
import os
import psycopg2
from psycopg2 import sql

from logs import logger


def get_connection():
    """Create and return a PostgreSQL connection."""
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ.get("DB_NAME", "your_db_name"),
        user=os.environ.get("DB_USER", "your_user"),
        password=os.environ.get("DB_PASSWORD", "your_password"),
    )


def create_table(table_name: str):
    """Create the table if it doesn't exist (requires pgvector extension)."""
    conn = get_connection()
    cur = conn.cursor()
    # Create the pgvector extension
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Build SQL safely with psycopg2.sql
    query = sql.SQL(
        """
        CREATE TABLE IF NOT EXISTS {table} (
            id SERIAL PRIMARY KEY,
            file_name TEXT,
            section TEXT,
            paragraph_id INT,
            content TEXT,
            embedding vector(768)
        );
    """
    ).format(table=sql.Identifier(table_name))

    cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"✅ Table ready: {table_name}")


def check_table_exists(table_name: str):
    """Check if the policy_paragraphs table exists."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = %s
        );
    """,
        (table_name,),
    )
    exists = cur.fetchone()[0]
    cur.close()
    conn.close()
    return exists


if __name__ == "__main__":
    create_table("policy_procedure")
    print("Does table exist?", check_table_exists("policy_procedure"))
