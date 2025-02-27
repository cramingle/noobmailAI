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
import os
import logging
import re
from scheduler_service import NewsletterSchedulerService
from datetime import datetime
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="SimpleMail AI")

# Get allowed origins from environment or use defaults
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS", 
    "http://localhost:5173,http://localhost:3000,https://noobmail.ai,https://noobmail-ai.vercel.app"
).split(",")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Allow both dev and production
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

class ContextFile(BaseModel):
    name: str
    content: str
    type: str

class ChatRequest(BaseModel):
    prompt: str
    context: Optional[List[ChatMessage]] = None
    system_prompt: Optional[str] = None
    contextFiles: Optional[List[ContextFile]] = None

class NewsletterRequest(BaseModel):
    topic: str
    content_details: Dict[str, Any]
    style_preferences: Optional[Dict[str, Any]] = None

class QuotaResponse(BaseModel):
    remaining_chats: int
    max_chats: int
    remaining_emails: int
    max_emails: int

class ScheduleNewsletterRequest(BaseModel):
    name: str
    description: Optional[str] = None
    template_content: str
    recipient_group: str
    frequency: str  # 'monthly' or 'weekly'
    start_date: datetime

# Email quota tracking
email_count = 0
max_email_count = 1  # Only allow one email per IP

scheduler_service = NewsletterSchedulerService()

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
    try:
        # Log the request for debugging
        logger.info(f"Chat request received with prompt: {request.prompt[:50]}...")
        if request.contextFiles:
            logger.info(f"Context files included: {[cf.name for cf in request.contextFiles]}")
        
        # Build context from previous messages
        context = request.context or []
        
        # Create a custom system prompt that emphasizes the importance of context files
        custom_system_prompt = """You are an AI assistant specialized in helping users create newsletters and email content.
Your goal is to provide helpful, accurate, and creative responses to user queries about newsletter creation.

IMPORTANT: USER CONTEXT FILES
The user may provide context files that contain important information. These files are crucial for understanding
the user's needs and generating appropriate responses. Pay special attention to any context files mentioned
with @filename syntax or by name in the user's message.
"""
        
        # Add context files to the system prompt for better understanding
        if request.contextFiles:
            custom_system_prompt += "\n\nThe following context files have been provided:\n"
            
            for cf in request.contextFiles:
                custom_system_prompt += f"\n--- BEGIN CONTEXT FILE: {cf.name} ---\n"
                custom_system_prompt += cf.content
                custom_system_prompt += f"\n--- END CONTEXT FILE: {cf.name} ---\n"
            
            # Check for @filename mentions in the prompt
            mention_pattern = r'@(\S+)'
            mentions = re.findall(mention_pattern, request.prompt)
            
            # Add mentioned context files as user messages for better visibility
            for mention in mentions:
                for cf in request.contextFiles:
                    if cf.name.lower() == mention.lower():
                        if not context:
                            context = []
                        context.append({
                            "role": "user",
                            "content": f"Here is the content of {cf.name} that I'm referring to with @{mention}:\n\n{cf.content}"
                        })
                        break
            
            # Also add the first context file as a user message if it's relevant to the current prompt
            if not any(mentions) and request.contextFiles:
                for cf in request.contextFiles:
                    if request.prompt.lower().find(cf.name.lower()) >= 0:
                        if not context:
                            context = []
                        context.append({
                            "role": "user",
                            "content": f"Here is the content of {cf.name} that I'm referring to:\n\n{cf.content}"
                        })
                        break
        
        # Generate response
        response = ai_service.generate_response(
            prompt=request.prompt,
            context=context,
            system_prompt=custom_system_prompt
        )
        
        return response
    except Exception as e:
        logger.error(f"Error in chat_with_ai: {str(e)}")
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

@app.post("/schedule-newsletter")
async def schedule_newsletter(request: ScheduleNewsletterRequest):
    """Schedule a recurring newsletter"""
    try:
        result = await scheduler_service.schedule_newsletter(
            name=request.name,
            description=request.description,
            template_content=request.template_content,
            recipient_group=request.recipient_group,
            frequency=request.frequency,
            start_date=request.start_date
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scheduled-newsletters")
async def get_scheduled_newsletters():
    """Get all scheduled newsletters"""
    session = Session()
    try:
        schedules = session.query(NewsletterSchedule).all()
        return [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "recipient_group": s.recipient_group,
                "frequency": s.frequency,
                "next_send_date": s.next_send_date,
                "last_sent_date": s.last_sent_date,
                "is_active": s.is_active
            }
            for s in schedules
        ]
    finally:
        session.close()

@app.put("/schedule-newsletter/{schedule_id}")
async def update_newsletter_schedule(schedule_id: int, request: ScheduleNewsletterRequest):
    """Update a scheduled newsletter"""
    session = Session()
    try:
        schedule = session.query(NewsletterSchedule).get(schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        schedule.name = request.name
        schedule.description = request.description
        schedule.template_content = request.template_content
        schedule.recipient_group = request.recipient_group
        schedule.frequency = request.frequency
        schedule.next_send_date = request.start_date
        
        session.commit()
        
        # Update the scheduler job
        scheduler_service._add_newsletter_job(schedule)
        
        return {"status": "success", "message": "Schedule updated successfully"}
    finally:
        session.close()

@app.delete("/schedule-newsletter/{schedule_id}")
async def delete_newsletter_schedule(schedule_id: int):
    """Delete a scheduled newsletter"""
    session = Session()
    try:
        schedule = session.query(NewsletterSchedule).get(schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        # Remove the scheduler job
        job_id = f"newsletter_{schedule_id}"
        scheduler_service.scheduler.remove_job(job_id)
        
        # Delete from database
        session.delete(schedule)
        session.commit()
        
        return {"status": "success", "message": "Schedule deleted successfully"}
    finally:
        session.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 