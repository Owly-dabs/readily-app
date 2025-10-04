from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from typing import List, Dict, Any
import logging

# Import our compliance question extractor
from extractor.extract import extract_compliance_questions

app = FastAPI(title="Compliance Audit API", version="1.0.0")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextRequest(BaseModel):
   text: str


class QuestionResponse(BaseModel):
   question_id: int
   question_text: str


class AuditResponse(BaseModel):
   success: bool
   questions: List[QuestionResponse]
   count: int
   message: str


@app.get("/")
async def root():
   return {"status": "ok", "service": "Compliance Audit API"}


@app.post("/audit", response_model=AuditResponse)
def text_audit(request: TextRequest):
   """
   Extract compliance and audit questions from the provided text.

   This endpoint uses AI to analyze the input text and extract any
   audit or compliance related questions found within it.
   """
   try:
       logger.info("Received audit request")

       if not request.text or not request.text.strip():
           raise HTTPException(status_code=400, detail="Text cannot be empty")

       # Extract compliance questions using our AI function
       questions = extract_compliance_questions(request.text)

       logger.info(f"Successfully extracted {len(questions)} questions")

       return AuditResponse(
           success=True,
           questions=questions,
           count=len(questions),
           message=f"Successfully extracted {len(questions)} compliance questions"
       )

   except ValueError as e:
       logger.error(f"Validation error: {e}")
       raise HTTPException(status_code=400, detail=str(e))
   except Exception as e:
       logger.error(f"Error processing audit request: {e}")
       raise HTTPException(
           status_code=500,
           detail="Internal server error occurred while processing the text"
       )


if __name__ == "__main__":
    uvicorn.run(app, port=8080, host="0.0.0.0")
