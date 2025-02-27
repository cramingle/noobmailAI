from fastapi import FastAPI, HTTPException # type: ignore
from pydantic import BaseModel # type: ignore
from typing import Optional, List, Dict, Any
from ai_service import AIService

app = FastAPI()
ai_service = AIService()

class ChatRequest(BaseModel):
    message: str
    email_type: str = "newsletter"
    context: Optional[List[Dict[str, str]]] = None

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Pass email type to AI service
        response = ai_service.generate_response(
            prompt=request.message,
            context=request.context,
            email_type=request.email_type
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-email")
async def generate_email(request: Dict[str, Any]):
    try:
        # Generate email based on type
        response = ai_service.generate_newsletter_html(
            topic=request.get("topic", ""),
            content_details=request.get("content_details", {}),
            style_preferences=request.get("style_preferences"),
            email_type=request.get("email_type", "newsletter")
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 