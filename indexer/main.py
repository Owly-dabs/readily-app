from indexer.db import get_connection
from indexer.insert import (
    save_results_to_db,
    check_results_in_db,
    clear_table,
    save_policyprocedure_to_db,
)
from indexer.parse import extract_points, extract_purpose, extract_policy_and_procedure
from logs import logger


def insert_one_pdf(file_path: str):
    """Parse a PDF and insert its contents into the database."""
    conn = get_connection()
    cur = conn.cursor()
    logger.info(f"Connected to DB.")

    try:
        results = extract_points(file_path)
    except Exception as e:
        logger.warning(f"Failed to extract points from {file_path}: {e}")
        return

    save_results_to_db(cur, results, "policy_paragraphs")

    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"✅ Inserted {len(results)} rows into policy_paragraphs")


def insert_pdf_all(cur, file_path: str):
    """Parse a PDF and insert its contents into the database."""
    try:
        results = extract_points(file_path)
    except Exception as e:
        logger.warning(f"Failed to extract points from {file_path}: {e}")
        return

    save_results_to_db(cur, results, "policy_paragraphs")


def insert_pdf_purpose(cur, file_path: str):
    """Parse a PDF and insert its contents into the database."""
    try:
        results = extract_purpose(file_path)
    except Exception as e:
        logger.warning(f"Failed to extract points from {file_path}: {e}")
        return

    save_results_to_db(cur, results, "policy_purpose")


def insert_purpose_pdfs_in_dir(directory_path: str):
    """Parse all PDFs in a directory and insert their contents into the database."""
    from pathlib import Path

    pdf_files = list(Path(directory_path).glob("*.pdf"))
    conn = get_connection()
    cur = conn.cursor()
    logger.info(f"Connected to DB.")

    total = len(pdf_files)
    for pdf_file in pdf_files:
        logger.info(f"Processing {pdf_file} ({pdf_files.index(pdf_file)+1}/{total})")
        insert_pdf_purpose(cur, str(pdf_file))
        conn.commit()

    cur.close()
    conn.close()
    logger.info(f"✅ Inserted {len(pdf_files)} files into policy_purpose")


def insert_pdf_policyprocedure(cur, file_path: str):
    """Parse a PDF and insert its contents into the database."""
    try:
        results = extract_policy_and_procedure(file_path)
    except Exception as e:
        logger.warning(f"Failed to extract points from {file_path}: {e}")
        return

    save_policyprocedure_to_db(cur, results, "policy_procedure")


def insert_policyprocedure_pdfs_in_dir(directory_path: str):
    """Parse all PDFs in a directory and insert their contents into the database."""
    from pathlib import Path

    pdf_files = list(Path(directory_path).glob("*.pdf"))
    conn = get_connection()
    cur = conn.cursor()
    logger.info(f"Connected to DB.")

    total = len(pdf_files)
    for pdf_file in pdf_files:
        logger.info(f"Processing {pdf_file} ({pdf_files.index(pdf_file)+1}/{total})")
        insert_pdf_policyprocedure(cur, str(pdf_file))
        conn.commit()

    cur.close()
    conn.close()
    logger.info(f"✅ Inserted {len(pdf_files)} files into policy_procedure")
