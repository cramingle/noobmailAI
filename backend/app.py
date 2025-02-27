from fastapi import FastAPI, HTTPException # type: ignore
from pydantic import BaseModel # type: ignore
from typing import Optional, List, Dict, Any
from local_ai_service import chat_with_ai, generate_newsletter

app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str
    email_type: str = "professional"
    context: Optional[List[Dict[str, str]]] = None
    system_prompt: Optional[str] = None

@app.post("/ai/chat")
async def chat(request: ChatRequest):
    try:
        response = await chat_with_ai(request)
        return response
    except Exception as e:
        print(f"Error in /ai/chat: {str(e)}")  # Add logging
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/generate-newsletter")
async def generate_email(request: Dict[str, Any]):
    try:
        response = await generate_newsletter(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 