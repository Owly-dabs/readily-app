from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from extractor.extract import extract_compliance_questions

app = FastAPI()


class TextRequest(BaseModel):
    text: str


@app.get("/")
async def root():
    return {"status": "ok"}


@app.post("/audit")
def text_audit(request: TextRequest):
    try:
        questions = extract_compliance_questions(request.text)
        return {"questions": questions}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


if __name__ == "__main__":
    uvicorn.run(app, port=8080, host="0.0.0.0")
