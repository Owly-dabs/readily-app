from indexer.db import get_connection
from indexer.embed import embed_text
from logs import logger


def save_results_to_db(cur, results, table_name: str):
    """
    Insert a list of dicts into the database.
    Each result dict should have keys:
    file_name, section, paragraph_id, content
    """
    # conn = get_connection()
    # cur = conn.cursor()
    # logger.info(f"Connected to DB.")

    for r in results:
        embedding = embed_text(r["content"])
        cur.execute(
            f"""
            INSERT INTO {table_name}
            (file_name, section, paragraph_id, content, embedding)
            VALUES (%s, %s, %s, %s, %s)
        """,
            (r["file_name"], r["section"], r["paragraph_id"], r["content"], embedding),
        )

    logger.info(f"Inserted {len(results)} rows, committing...")

    # conn.commit()
    # cur.close()
    # conn.close()
    # logger.info(f"✅ Inserted {len(results)} rows into policy_paragraphs")


def save_policyprocedure_to_db(cur, results, table_name: str):
    """
    Insert a list of dicts into the database.
    Each result dict should have keys:
    file_name, section, paragraph_id, content
    """

    for r in results:
        cur.execute(
            f"""
            INSERT INTO {table_name}
            (file_name, section, content)
            VALUES (%s, %s, %s)
        """,
            (r["file_name"], r["section"], r["content"]),
        )

    logger.info(f"Inserted {len(results)} rows, committing...")


def clear_table(table_name: str):
    """Delete all rows from the specified table."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table_name};")
    deleted = cur.rowcount
    logger.info(f"Cleared table {table_name}, deleted {deleted} rows.")
    conn.commit()
    cur.close()
    conn.close()


def check_results_in_db(table_name: str) -> int:
    """Check how many rows are in the specified table."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count
