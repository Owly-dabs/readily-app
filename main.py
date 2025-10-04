from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel

app = FastAPI()


class TextRequest(BaseModel):
    text: str


@app.get("/")
async def root():
    return {"status": "ok"}


@app.post("/audit")
def text_audit(request: TextRequest):
    return {"received_text": request.text}


if __name__ == "__main__":
    uvicorn.run(app, port=8080, host="0.0.0.0")
