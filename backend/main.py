from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid, formataddr
from email_service import send_email, improve_content
from ai_service import ai_service

app = FastAPI(title="SimpleMail AI")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Svelte dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class SmtpConfig(BaseModel):
    server: str
    port: str
    email: EmailStr
    password: str
    name: str

class Recipient(BaseModel):
    name: str
    email: EmailStr
    organization: Optional[str] = None

class EmailContent(BaseModel):
    content: str
    recipients: List[Recipient]
    smtp: SmtpConfig
    use_ai: bool = False

class ContentRequest(BaseModel):
    content: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    prompt: str
    context: Optional[List[ChatMessage]] = None
    system_prompt: Optional[str] = None

class NewsletterRequest(BaseModel):
    topic: str
    content_details: Dict[str, Any]
    style_preferences: Optional[Dict[str, Any]] = None

class QuotaResponse(BaseModel):
    remaining_chats: int
    max_chats: int
    remaining_emails: int
    max_emails: int

# Email quota tracking
email_count = 0
max_email_count = 1  # Only allow one email per IP

@app.post("/test-smtp")
async def test_smtp(config: SmtpConfig):
    try:
        # Try to establish SMTP connection
        if config.port == "465":
            server = smtplib.SMTP_SSL(config.server, int(config.port))
        else:
            server = smtplib.SMTP(config.server, int(config.port))
            server.starttls()
        
        server.login(config.email, config.password)
        server.quit()
        return {"status": "success", "message": "SMTP configuration is valid"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/send-email")
async def send_email_endpoint(email_content: EmailContent):
    global email_count
    
    try:
        # Check if email quota is exceeded
        if email_count >= max_email_count:
            return {
                "status": "quota_exceeded",
                "message": "You've reached your email sending limit. Join our waitlist for continued access!",
                "show_waitlist": True
            }
        
        content = email_content.content
        if email_content.use_ai:
            content = improve_content(content)
        
        result = send_email(
            content=content,
            recipients=[dict(r) for r in email_content.recipients],
            smtp_config=dict(email_content.smtp),
            campaign_name="newsletter"
        )
        
        # Increment email count after successful send
        email_count += 1
        
        return {
            "status": "success",
            "message": f"Successfully sent {result['successful_sends']} emails",
            "failed": result['failed_sends'],
            "remaining_emails": max_email_count - email_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/improve-content")
async def improve_content_endpoint(content: ContentRequest):
    try:
        improved = improve_content(content.content)
        return {"improved_content": improved}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New AI endpoints
@app.post("/ai/chat")
async def chat_with_ai(request: ChatRequest):
    """
    Chat with the AI to get help with newsletter creation.
    """
    try:
        # Convert context to the format expected by the AI service
        context = None
        if request.context:
            context = [{"role": msg.role, "content": msg.content} for msg in request.context]
        
        # Generate response
        response = ai_service.generate_response(
            prompt=request.prompt,
            context=context,
            system_prompt=request.system_prompt
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/generate-newsletter")
async def generate_newsletter(request: NewsletterRequest):
    """
    Generate a complete newsletter HTML based on the provided topic and details.
    """
    try:
        response = ai_service.generate_newsletter_html(
            topic=request.topic,
            content_details=request.content_details,
            style_preferences=request.style_preferences
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/quota")
async def get_quota():
    """
    Get the current usage quota for the user.
    """
    return {
        "remaining_chats": ai_service.max_chat_count - ai_service.chat_count,
        "max_chats": ai_service.max_chat_count,
        "remaining_emails": max_email_count - email_count,
        "max_emails": max_email_count
    }

@app.post("/reset-quota")
async def reset_quota():
    """
    Reset the quota for testing purposes.
    In production, this would be protected and only used by admins.
    """
    global email_count
    email_count = 0
    ai_service.reset_chat_count()
    
    return {
        "status": "success",
        "message": "Quota has been reset"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 