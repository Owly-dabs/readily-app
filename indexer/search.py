from indexer.db import get_connection
from indexer.embed import embed_text
from datamodels import PolicyRow
from logs import logger


def search_similar_purpose(query: str, top_k: int = 3):
    """
    Perform semantic similarity search against stored paragraphs,
    limited to the 'PURPOSE' sections.
    Args:
        query: User's text query
        top_k: Number of results to return
    Returns:
        List of PolicyRow objects
    """
    query_vector = embed_text(query)

    conn = get_connection()
    cur = conn.cursor()

    # Only search within PURPOSE sections
    cur.execute(
        """
        SELECT
            file_name,
            section,
            paragraph_id,
            content,
            1 - (embedding <#> %s::vector) AS similarity
        FROM policy_purpose
        WHERE UPPER(section) LIKE '%%PURPOSE%%'
        ORDER BY embedding <-> %s::vector
        LIMIT %s;
    """,
        (query_vector, query_vector, top_k),
    )

    results = cur.fetchall()
    cur.close()
    conn.close()

    formatted = []
    for r in results:
        policy_row = PolicyRow(
            file_name=r[0],
            section=r[1],
            paragraph_id=r[2],
            content=r[3]
        )
        similarity = float(r[4])
        logger.info(f"Similarity match: {policy_row.file_name} - {policy_row.section} (similarity: {similarity:.3f})")
        formatted.append(policy_row)

    return formatted


def search_similar(query: str, top_k: int = 3):
    """
    Perform semantic similarity search against stored paragraphs.
    Args:
        query: User's text query
        top_k: Number of results to return
    Returns:
        List of PolicyRow objects
    """
    query_vector = embed_text(query)

    conn = get_connection()
    cur = conn.cursor()

    # The "<->" operator computes vector distance; lower = more similar
    cur.execute(
        """
        SELECT
            file_name,
            section,
            paragraph_id,
            content,
            1 - (embedding <#> %s::vector) AS similarity
        FROM policy_paragraphs
        ORDER BY embedding <-> %s::vector
        LIMIT %s;
    """,
        (query_vector, query_vector, top_k),
    )

    results = cur.fetchall()
    cur.close()
    conn.close()

    formatted = []
    for r in results:
        policy_row = PolicyRow(
            file_name=r[0],
            section=r[1],
            paragraph_id=r[2],
            content=r[3]
        )
        similarity = float(r[4])
        logger.info(f"Similarity match: {policy_row.file_name} - {policy_row.section} (similarity: {similarity:.3f})")
        formatted.append(policy_row)

    return formatted


def get_policyprocedure(file_path: str):
    """Fetch the policy and procedure sections from the policy_procedure table in db."""
    conn = get_connection()
    cur = conn.cursor()

    # Fetch all policy and procedure sections for the given file
    cur.execute(
        """
        SELECT
            file_name,
            section,
            content
        FROM policy_procedure
        WHERE file_name = %s
    """,
        (file_path,)
    )

    results = cur.fetchall()
    cur.close()
    conn.close()

    formatted = [
        PolicyRow(
            file_name=r[0],
            section=r[1],
            content=r[2]
        )
        for r in results
    ]
    return formatted


if __name__ == "__main__":
    # Example usage
    query = "Does the P&P state that the MCP must respond to retrospective requests no longer than 14 calendar days from receipt?"
    results = search_similar_purpose(query, top_k=5)
    print("\n🔍 Top Matches:")
    for i, r in enumerate(results, 1):
        print(f"\n{i}. [{r.file_name}] {r.section}")
        print(f"{r.content[:400]}{'...' if len(r.content) > 400 else ''}")
