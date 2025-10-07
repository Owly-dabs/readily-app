from google import genai
import json
import re
from logs import logger
from typing import List, Dict, Optional
from datamodels import ResponseItem

client = genai.Client()


def extract_questions(text: str) -> List[ResponseItem]:
    """
    Extracts numbered questions from text and returns them as ResponseItem objects.
    """
    pattern = r"\d+\.\s*(.+?\?)"
    matches = re.findall(pattern, text, flags=re.DOTALL)

    responses = []
    for i, q in enumerate(matches, start=1):
        cleaned_q = " ".join(q.split())  # normalize whitespace
        responses.append(ResponseItem(id=i, requirement=cleaned_q))
    return responses


def extract_compliance_questions(text: str) -> List[ResponseItem]:
    """
    Extract audit or compliance questions from the given text using Gemini AI.

    Args:
        text (str): The input text to analyze for compliance questions

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing id and requirement

    Raises:
        ValueError: If text is empty or None
        json.JSONDecodeError: If the model response is not valid JSON
        Exception: For other API or processing errors
    """
    # Input validation
    if not text or not text.strip():
        raise ValueError("Input text cannot be empty")

    # Clean and prepare the text
    cleaned_text = _preprocess_text(text)

    # Create the prompt
    prompt = f"""
You are an expert compliance officer tasked with extracting audit and compliance questions from text.

Please analyze the following text and extract ALL audit or compliance related questions.
Focus on questions that would be relevant for:
- Regulatory compliance audits
- Internal compliance reviews
- Risk assessments
- Policy adherence checks
- Control testing
- Governance reviews

Return ONLY a valid JSON array with objects in this exact format:
[{{"id": 1, "requirement": "What is the company's policy on data retention?"}}]

Rules:
- Extract questions as they appear in the text, don't rephrase them
- Include the question mark if present in the original text
- Number questions sequentially starting from 1
- Only include actual questions, not statements
- If no questions are found, return an empty array []
- Do NOT include any explanation or additional text, only the JSON array

Text to analyze:
{cleaned_text}
"""

    try:
        # Generate response from Gemini
        logger.info("Generating content from Gemini model...")
        response = client.models.generate_content(
            model="gemini-flash-latest", contents=prompt
        )

        if not response or not response.text:
            logger.warning("Empty response from model")
            return []

        # Clean the response text (remove markdown formatting if present)
        cleaned_response = _clean_model_response(response.text)

        # Parse JSON response
        questions = json.loads(cleaned_response)

        # Validate response format
        if not isinstance(questions, list):
            logger.error(f"Expected list from model, got {type(questions)}")
            return []

        # Validate each question object
        validated_questions = []
        for i, question in enumerate(questions, 1):
            if _is_valid_question(question):
                # Ensure id matches the sequential order
                question["id"] = i
                # Validate that we can create a ResponseItem from this data
                try:
                    ResponseItem(**question)
                    validated_questions.append(question)
                except Exception as e:
                    logger.warning(
                        f"Skipping question that cannot be converted to ResponseItem: {question}, error: {e}"
                    )
            else:
                logger.warning(f"Skipping invalid question format: {question}")

        logger.info(
            f"Successfully extracted {len(validated_questions)} compliance questions"
        )
        return [ResponseItem(**question) for question in validated_questions]

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        logger.error(f"Response text: {response.text if response else 'No response'}")
        raise json.JSONDecodeError(
            f"Invalid JSON response from model: {e}", e.doc, e.pos
        )
    except Exception as e:
        logger.error(f"Error extracting compliance questions: {e}")
        raise Exception(f"Failed to extract compliance questions: {str(e)}")


def _preprocess_text(text: str) -> str:
    """Clean and prepare text for analysis."""
    if not text:
        return ""

    # Remove extra whitespace and normalize line endings
    cleaned = re.sub(r"\n+", "\n", text.strip())
    cleaned = re.sub(r"[ \t]+", " ", cleaned)

    # Remove page numbers or headers that might interfere
    cleaned = re.sub(r"^\d+\s*$", "", cleaned, flags=re.MULTILINE)

    return cleaned


def _clean_model_response(response_text: str) -> str:
    """Clean the model's response text."""
    if not response_text:
        return ""

    # Remove markdown code block formatting if present
    cleaned = re.sub(r"```json\s*", "", response_text)
    cleaned = re.sub(r"```\s*$", "", cleaned)

    # Remove any leading/trailing whitespace
    cleaned = cleaned.strip()

    return cleaned


def _is_valid_question(question: Dict) -> bool:
    """Validate that a question object has the required format."""
    if not isinstance(question, dict):
        return False

    if "requirement" not in question:
        return False

    question_text = question.get("requirement", "").strip()
    if not question_text:
        return False

    # Check if it looks like a question (has question mark or question words)
    question_indicators = [
        "?",
        "what",
        "how",
        "when",
        "where",
        "why",
        "who",
        "which",
        "do",
        "does",
        "did",
        "is",
        "are",
        "was",
        "were",
        "can",
        "could",
        "should",
        "would",
        "will",
    ]
    has_question_mark = "?" in question_text.lower()
    has_question_word = any(
        word in question_text.lower() for word in question_indicators[:11]
    )  # First 11 are question words

    return has_question_mark or has_question_word


# Example usage and testing function
def test_extraction():
    """Test function for the compliance question extraction."""
    sample_text = """
   Company Policy Review

   1. What is the current data retention policy?
   2. How often are security audits conducted?
   3. Are all employees trained on compliance procedures?
   4. When was the last risk assessment completed?

   Additional Information:
   The compliance team meets monthly.
   All policies are reviewed annually.
   """

    try:
        questions = extract_compliance_questions(sample_text)
        print(f"Extracted {len(questions)} questions:")
        for question in questions:
            print(f"  {question.id}: {question.requirement}")
        return questions
    except Exception as e:
        print(f"Error during testing: {e}")
        return []


if __name__ == "__main__":
    # Run test if script is executed directly
    test_extraction()
