import fitz  # PyMuPDF
import re
from pathlib import Path
from typing import List, Dict
from logs import logger

logger.setLevel("DEBUG")


def extract_policy_and_procedure(pdf_path: str) -> str:
    """
    Extracts and returns the combined text of the POLICY and PROCEDURE sections
    from a CalOptima-style policy PDF.

    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        str: Combined text from POLICY and PROCEDURE sections.
    """
    pdf_path = Path(pdf_path)

    # ---- Read entire PDF ----
    with fitz.open(pdf_path) as doc:
        full_text = "\n".join(page.get_text("text") for page in doc)

    # ---- Normalize whitespace ----
    full_text = re.sub(r"\r", "", full_text)
    full_text = re.sub(r"[ \t]+", " ", full_text)
    full_text = re.sub(r"\n{3,}", "\n\n", full_text)
    full_text = re.sub(r"\n\s*\n", "\n\n", full_text)
    full_text = full_text.strip()

    # ---- Regex pattern to capture POLICY and PROCEDURE ----
    # This captures the POLICY section up to PROCEDURE, and PROCEDURE up to ATTACHMENT(S)
    pattern = re.compile(
        r"II\.\s*POLICY(?P<policy>.*?)"
        r"III\.\s*PROCEDURE(?P<procedure>.*?)"
        r"I(V)?\.\s*ATTACHMENT\(S\)",
        flags=re.S | re.I,
    )

    match = pattern.search(full_text)
    if not match:
        raise ValueError(f"Could not find POLICY / PROCEDURE sections in {pdf_path}")

    # ---- Extract and combine ----
    policy_text = match.group("policy").strip()
    procedure_text = match.group("procedure").strip()

    combined_text = f"{policy_text}\n\n{procedure_text}"
    logger.debug(f"Length of text: {len(combined_text)} characters")
    return combined_text


def extract_purpose(pdf_path: str) -> List[Dict]:
    """
    Extracts three main sections (Purpose, Policy, Procedure) and splits each into paragraphs.
    Returns a list of {file_name, section, paragraph_id, content}.
    """
    pdf_path = Path(pdf_path)
    file_name = pdf_path.name

    # ---- Read entire PDF ----
    with fitz.open(pdf_path) as doc:
        full_text = "\n".join(page.get_text("text") for page in doc)

    # ---- Normalize spacing ----
    full_text = re.sub(r"\r", "", full_text)
    full_text = re.sub(r"[ \t]+", " ", full_text)
    full_text = re.sub(r"\n{3,}", "\n\n", full_text)  # collapse excessive newlines
    full_text = re.sub(r"\n\s*\n", "\n\n", full_text)  # collapse excessive newlines
    full_text = full_text.strip()

    # ---- Split into main sections ----
    # Use non-greedy matching so each section captures up to the next Roman numeral
    pattern = re.compile(
        r"I\.\s*PURPOSE(?P<purpose>.*?)"
        r"II\.\s*POLICY(?P<policy>.*?)",
        flags=re.S | re.I,
    )

    match = pattern.search(full_text)
    if not match:
        raise ValueError(
            f"Could not find PURPOSE / POLICY / PROCEDURE sections in {pdf_path}"
        )

    sections = {
        "purpose": match.group("purpose").strip(),
    }
    
    logger.debug(f"purpose: {sections['purpose'][:30]}...")
    logger.info(f"Extracted sections: {', '.join(sections.keys())}")

    # ---- Split each section by paragraph ----
    results = []
    for section_name, section_text in sections.items():
        # Split paragraphs and strip whitespace
        paragraphs = [p.strip() for p in section_text.split("\n\n") if p.strip()]

        logger.debug(f"Found {len(paragraphs)} paragraphs in section {section_name}")

        # Merge short paragraphs
        merged_paragraphs = []
        i = 0
        while i < len(paragraphs):
            current = paragraphs[i]

            if len(current) < 200 and i + 1 < len(paragraphs):
                # Merge with next paragraph
                merged = current + "\n\n" + paragraphs[i + 1]
                merged_paragraphs.append(merged)
                i += 2  # Skip the next one
            else:
                merged_paragraphs.append(current)
                i += 1

        logger.debug(f"Found {len(paragraphs)} paragraphs in section {section_name}")

        # Add merged paragraphs to results
        for i, paragraph in enumerate(merged_paragraphs, start=1):
            results.append(
                {
                    "file_name": file_name,
                    "section": section_name,
                    "paragraph_id": i,
                    "content": paragraph,
                }
            )

    logger.info(f"Extracted {len(results)} paragraphs from {file_name}")
    return results


def extract_points(pdf_path: str) -> List[Dict]:
    """
    Extracts three main sections (Purpose, Policy, Procedure) and splits each into paragraphs.
    Returns a list of {file_name, section, paragraph_id, content}.
    """
    pdf_path = Path(pdf_path)
    file_name = pdf_path.name

    # ---- Read entire PDF ----
    with fitz.open(pdf_path) as doc:
        full_text = "\n".join(page.get_text("text") for page in doc)

    # ---- Normalize spacing ----
    full_text = re.sub(r"\r", "", full_text)
    full_text = re.sub(r"[ \t]+", " ", full_text)
    full_text = re.sub(r"\n{3,}", "\n\n", full_text)  # collapse excessive newlines
    full_text = re.sub(r"\n\s*\n", "\n\n", full_text)  # collapse excessive newlines
    full_text = full_text.strip()

    # ---- Split into main sections ----
    # Use non-greedy matching so each section captures up to the next Roman numeral
    pattern = re.compile(
        r"I\.\s*PURPOSE(?P<purpose>.*?)"
        r"II\.\s*POLICY(?P<policy>.*?)"
        r"III\.\s*PROCEDURE(?P<procedure>.*?)"
        r"I(V)?\.\s*ATTACHMENT\(S\)(?P<attachment>.*?)",
        flags=re.S | re.I,
    )

    match = pattern.search(full_text)
    if not match:
        raise ValueError(
            f"Could not find PURPOSE / POLICY / PROCEDURE sections in {pdf_path}"
        )

    sections = {
        "purpose": match.group("purpose").strip(),
        "policy": match.group("policy").strip(),
        "procedure": match.group("procedure").strip(),
    }
    logger.debug(f"purpose: {sections['purpose'][:30]}...")
    logger.debug(f"policy: {sections['policy'][:30]}...")
    logger.info(f"Extracted sections: {', '.join(sections.keys())}")

    # ---- Split each section by paragraph ----
    results = []
    for section_name, section_text in sections.items():
        # Split paragraphs and strip whitespace
        paragraphs = [p.strip() for p in section_text.split("\n\n") if p.strip()]

        logger.debug(f"Found {len(paragraphs)} paragraphs in section {section_name}")

        # Merge short paragraphs
        merged_paragraphs = []
        i = 0
        while i < len(paragraphs):
            current = paragraphs[i]

            if len(current) < 200 and i + 1 < len(paragraphs):
                # Merge with next paragraph
                merged = current + "\n\n" + paragraphs[i + 1]
                merged_paragraphs.append(merged)
                i += 2  # Skip the next one
            else:
                merged_paragraphs.append(current)
                i += 1

        logger.debug(f"Found {len(paragraphs)} paragraphs in section {section_name}")

        # Add merged paragraphs to results
        for i, paragraph in enumerate(merged_paragraphs, start=1):
            results.append(
                {
                    "file_name": file_name,
                    "section": section_name,
                    "paragraph_id": i,
                    "content": paragraph,
                }
            )

    logger.info(f"Extracted {len(results)} paragraphs from {file_name}")
    return results
