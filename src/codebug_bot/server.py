from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from .chatbot import chat_process

app = FastAPI(title="bics-chatbot")


class AnalyzeRequest(BaseModel):
    code: str
    apply_fix: bool = True


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    return chat_process(req.code, apply_fix=req.apply_fix)
