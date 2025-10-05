import os
import google.generativeai as genai
import re

from logs import logger

logger.setLevel("INFO")

# Configure API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def check_requirement(policy_text: str, requirement: str) -> dict:
    """
    Uses Google Gemini to determine if a requirement is met by a given policy+procedure text.
    If met, cites the relevant portion word-for-word.

    Args:
        policy_text (str): Combined policy and procedure section text.
        requirement (str): Compliance requirement or audit question.

    Returns:
        dict: { "requirement": str, "is_met": bool, "explanation": str, "citation": str }
    """
    model = genai.GenerativeModel("gemini-pro-latest")

    prompt = f"""
You are an expert compliance officer.

You are given:
1. A policy and procedure text.
2. A requirement that the policy must fulfill.

Your task:
- Determine if the requirement is **met** based on the policy text.
- If it is met, **quote the exact sentence(s)** from the text that serve as evidence.
- If not, explain briefly why it is not met.
- Always be objective and base your answer only on the given text.

---

**Requirement:**
{requirement}

**Policy + Procedure Text:**
\"\"\"{policy_text}\"\"\"

Respond in JSON with the following keys:
- "is_met": true or false
- "citation": exact quoted text if met (if any)
- "explanation": brief reasoning if not met (if any)
    """

    response = model.generate_content(prompt)

    # Try to parse model output safely
    text = response.text.strip()
    try:
        # If model outputs valid JSON
        import json
        logger.debug(f"Model output: {text}")
        cleaned = re.sub(r"^```(?:json)?", "", text.strip(), flags=re.IGNORECASE)
        cleaned = re.sub(r"```$", "", cleaned.strip())

        result = json.loads(cleaned)
    except Exception:
        # Fallback if model outputs plain text
        result = {"is_met": None, "citation": None, "explanation": None}

    result["requirement"] = requirement
    return result
