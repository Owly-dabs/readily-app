from indexer.db import get_connection
from indexer.embed import embed_text
from logs import logger

def save_results_to_db(cur, results):
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
        cur.execute("""
            INSERT INTO policy_paragraphs
            (file_name, section, paragraph_id, content, embedding)
            VALUES (%s, %s, %s, %s, %s)
        """, (r["file_name"], r["section"], r["paragraph_id"], r["content"], embedding))

    logger.info(f"Inserted {len(results)} rows, committing...")

    # conn.commit()
    # cur.close()
    # conn.close()
    # logger.info(f"✅ Inserted {len(results)} rows into policy_paragraphs")
    
def clear_table():
    """Delete all rows from the policy_paragraphs table."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM policy_paragraphs;")
    deleted = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"Cleared table, deleted {deleted} rows.")
    
def check_results_in_db():
    """Check how many rows are in the policy_paragraphs table."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM policy_paragraphs;")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count