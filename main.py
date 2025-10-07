from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel

from indexer.insert import check_results_in_db
from datamodels import ResponseItem, PolicyRow, TextRequest
from workflows import audit_main, audit_test, audit_one
from logs import logger

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/health")
async def health_check():
    # Connect to DB and perform a simple query to check health
    try:
        procedure_rows = check_results_in_db("policy_procedure")
        if not procedure_rows:
            return {"status": "error", "message": "No procedures found"}

        purpose_rows = check_results_in_db("policy_purpose")
        if not purpose_rows:
            return {"status": "error", "message": "No purposes found"}

        return {
            "status": "ok",
            "data": {"procedures": procedure_rows, "purposes": purpose_rows},
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/audit_one")
def text_audit_one(request: ResponseItem):
    try:
        response = audit_one(request)
        return {"response": response}

    except ValueError as ve:
        logger.error(f"ValueError: {ve}")
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/audit")
def text_audit(request: TextRequest):
    try:
        responses = audit_main(request)
        return {"responses": responses}

    except ValueError as ve:
        logger.error(f"ValueError: {ve}")
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


if __name__ == "__main__":
    uvicorn.run(app, port=8080, host="0.0.0.0")
