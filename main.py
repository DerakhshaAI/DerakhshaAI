from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from engine import DerakhshaEngine

BASE = Path(__file__).parent
app = FastAPI(title='Derakhsha AI')
engine = DerakhshaEngine()

class ChatRequest(BaseModel):
    message: str
    style: str = 'formal'

@app.get('/')
def home():
    return FileResponse(BASE / 'static' / 'index.html')

@app.post('/api/chat')
def chat(req: ChatRequest):
    return engine.answer(req.message, req.style)

@app.get('/api/tree')
def tree():
    return engine.tree_json()
