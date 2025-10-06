from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel

from extractor.extract import extract_compliance_questions
from extractor.cite import check_requirement
from indexer.search import search_similar_purpose, get_policyprocedure
from indexer.insert import check_results_in_db
from datamodels import ResponseItem, PolicyRow

app = FastAPI()


class TextRequest(BaseModel):
    text: str


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

        return {"status": "ok", "data": {"procedures": procedure_rows, "purposes": purpose_rows}}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/audit")
def text_audit(request: TextRequest):
    try:
        responses: list[ResponseItem] = extract_compliance_questions(request.text)
        for r in responses:
            policies: list[PolicyRow] = search_similar_purpose(r.requirement, top_k=3)
            policy_content: list[PolicyRow] = []

            for p in policies:
                proceduresRows = get_policyprocedure(p.file_name)
                policy_content.extend(proceduresRows)

            is_met_flag = False
            for policy in policy_content:
                check_result = check_requirement(policy.content, r.requirement)
                if check_result["is_met"]:
                    is_met_flag = True
                    r.is_met = True
                    r.file_name = policy.file_name
                    r.citation = check_result["citation"]
                    break
                
            if not is_met_flag:
                r.is_met = False
                r.citation = None
                r.explanation = "Documents reviewed: " + "; ".join([p.file_name for p in policies])
                
        return {"responses": responses}
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


if __name__ == "__main__":
    uvicorn.run(app, port=8080, host="0.0.0.0")
