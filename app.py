# -*- coding: utf-8 -*-
"""
API سرور درخشا — مناسب Railway
"""
from __future__ import annotations
import os
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from derakhsha.engine import DerakhshaEngine

engine = DerakhshaEngine()

app = FastAPI(
    title="درخشا",
    description="موتور هوش مصنوعی درخت دانش — گروک × احمدرضا ایزدی",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC = Path(__file__).parent / "static"
if STATIC.exists():
    app.mount("/assets", StaticFiles(directory=STATIC), name="assets")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    session_id: str = "default"
    style: Optional[str] = None  # colloquial | formal


class LearnRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    body: str = Field(..., min_length=1, max_length=100000)
    doc_type: str = "مقاله"
    keywords: Optional[List[str]] = None
    source: str = "user"


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)


@app.get("/")
def root():
    index = STATIC / "index.html"
    if index.exists():
        return FileResponse(index)
    return {
        "name": "درخشا",
        "version": "1.0.0",
        "creators": ["گروک", "احمدرضا ایزدی"],
        "docs": "/docs",
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "engine": "derakhsha", "version": "1.0.0"}


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        return engine.chat(req.message, session_id=req.session_id, style=req.style)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/learn")
def api_learn(req: LearnRequest):
    try:
        return engine.learn_document(
            title=req.title,
            body=req.body,
            doc_type=req.doc_type,
            keywords=req.keywords,
            source=req.source,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
def api_analyze(req: AnalyzeRequest):
    return engine.analyze_only(req.text)


@app.get("/api/branches")
def api_branches():
    return {"branches": engine.list_branches()}


@app.get("/api/tree")
def api_tree():
    return engine.tree.to_dict()


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
