from fastapi import FastAPI, HTTPException # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from pydantic import BaseModel # type: ignore
from typing import List, Optional, Dict, Any
import requests
import json
import re
from datetime import datetime
from sqlalchemy.orm import Session, sessionmaker # type: ignore
from models import ChatSession, ChatMessage, engine
import logging
import uvicorn # type: ignore
import os
from dotenv import load_dotenv # type: ignore

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ollama API Configuration
OLLAMA_API = os.getenv('OLLAMA_API_URL', 'http://localhost:11434/api/chat')
DEFAULT_SYSTEM_PROMPT = """You are an expert email writer and designer. When asked to create emails, ALWAYS respond with properly formatted HTML that includes modern, responsive design and styling.

Key requirements:
1. ALWAYS include complete HTML structure with <!DOCTYPE html>, <head>, and <body> tags
2. ALWAYS include embedded CSS in <style> tag with modern design principles
3. Use responsive design with media queries for mobile compatibility
4. Include professional color schemes and typography
5. Ensure proper spacing and layout using modern CSS
6. Add engaging visual hierarchy and white space

Example structure:
<!DOCTYPE html>
<html>
<head>
    <style>
        /* Modern, responsive CSS here */
    </style>
</head>
<body>
    /* Well-structured content here */
</body>
</html>

Remember: Every email response should be beautifully designed and ready to use."""

app = FastAPI()

# Create database session
SessionLocal = sessionmaker(bind=engine)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessageModel(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    prompt: str
    session_id: Optional[int] = None
    context: Optional[List[ChatMessageModel]] = None
    system_prompt: Optional[str] = None
    email_type: Optional[str] = "newsletter"  # Can be "newsletter" or "job_application"

class ChatSessionCreate(BaseModel):
    name: str
    email_type: str = "newsletter"

class NewsletterRequest(BaseModel):
    topic: str
    content_details: Dict[str, Any]
    style_preferences: Optional[Dict[str, Any]] = None

def validate_email_request(prompt: str, email_type: str = "newsletter") -> bool:
    """Validate if the request is related to email creation."""
    email_keywords = {
        "newsletter": [
            'newsletter', 'email', 'template', 'campaign',
            'header', 'footer', 'design', 'layout',
            'responsive', 'html', 'subject line', 'edm',
            'marketing email', 'email blast', 'mailing list'
        ],
        "job_application": [
            'job application', 'cover letter', 'job email',
            'application email', 'resume', 'cv', 'hiring manager',
            'recruiter', 'position', 'job opening', 'vacancy',
            'career', 'opportunity', 'employment', 'apply'
        ],
        "scholarship": [
            'scholarship', 'academic', 'application letter',
            'statement of purpose', 'motivation letter',
            'research proposal', 'grant application',
            'funding request', 'academic achievement',
            'educational background', 'study plan'
        ],
        "business": [
            'business proposal', 'partnership', 'collaboration',
            'meeting request', 'follow up', 'quotation',
            'professional service', 'business opportunity',
            'contract', 'agreement', 'business inquiry'
        ]
    }
    
    # If email type is specified, check those keywords
    if email_type in email_keywords:
        return any(keyword in prompt.lower() for keyword in email_keywords[email_type])
    
    # If type not specified or unknown, check all keywords
    all_keywords = [word for keywords in email_keywords.values() for word in keywords]
    return any(keyword in prompt.lower() for keyword in all_keywords)

def enforce_anti_spam_elements(html: str, email_type: str = "newsletter") -> str:
    """Ensure HTML includes all necessary anti-spam elements based on email type."""
    required_elements = {
        'viewport': '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        'content_type': '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
    }
    
    if email_type == "newsletter":
        required_elements.update({
            'unsubscribe': '<a href="{unsubscribe_url}" style="color: #666666; text-decoration: underline;">Unsubscribe</a>',
            'physical_address': '<p style="color: #666666; font-size: 12px;">{company_address}</p>',
            'permission_reminder': '<p style="color: #666666; font-size: 12px;">You received this email because you signed up for updates from {company_name}.</p>'
        })
    else:  # job_application
        required_elements.update({
            'signature': '''
                <div style="margin-top: 20px; color: #333333;">
                    <p style="margin: 0;">{full_name}</p>
                    <p style="margin: 5px 0;">{phone_number}</p>
                    <p style="margin: 0;">{email_address}</p>
                    <p style="margin: 5px 0;"><a href="{linkedin_url}" style="color: #0077B5; text-decoration: none;">LinkedIn Profile</a></p>
                    <p style="margin: 5px 0;"><a href="{portfolio_url}" style="color: #333333; text-decoration: none;">Portfolio</a></p>
                </div>
            ''',
            'ats_friendly': '<!-- ATS-friendly email structure -->'
        })
    
    for element_name, element_html in required_elements.items():
        if element_name not in html.lower():
            if 'body' in html:
                # Add before closing body tag
                html = html.replace('</body>', f'{element_html}</body>')
            else:
                # Append to the end
                html += element_html
    
    return html

def optimize_for_spam_filters(html: str) -> str:
    """Optimize HTML content to avoid spam filters."""
    # Remove potential spam trigger elements
    spam_patterns = [
        (r'<font[^>]*>', ''),  # Remove font tags
        (r'<blink[^>]*>.*?</blink>', ''),  # Remove blink tags
        (r'<marquee[^>]*>.*?</marquee>', ''),  # Remove marquee tags
        (r'(?i)free!|act now!|click here!|buy now!|order now!|limited time!', ''),  # Remove spam trigger phrases
        (r'[!]{2,}', '!'),  # Replace multiple exclamation marks
        (r'[$]{2,}', '$'),  # Replace multiple dollar signs
    ]
    
    for pattern, replacement in spam_patterns:
        html = re.sub(pattern, replacement, html)
    
    # Ensure proper text-to-HTML ratio
    if len(re.findall(r'<[^>]+>', html)) / len(html) > 0.3:
        # Too much HTML compared to text, add a warning comment
        html = '<!-- Warning: High HTML-to-text ratio may trigger spam filters -->\n' + html
    
    return html

def handle_ollama_error(error_text: str) -> str:
    """Convert technical error messages into user-friendly responses"""
    if "connection refused" in error_text.lower():
        return "I'm having trouble connecting to my language model right now. Please try again in a moment."
    elif "context length" in error_text.lower():
        return "Our conversation has gotten quite long. Let's start fresh so I can help you better."
    elif "rate limit" in error_text.lower():
        return "I'm processing quite a few requests right now. Please try again in a few seconds."
    else:
        return "I encountered an unexpected issue. Could you rephrase your request or try again?"

def format_chat_response(response_text: str, email_type: str = "newsletter") -> Dict[str, Any]:
    """Format the chat response, handling HTML content specially."""
    # Check if the response contains HTML-like content
    has_html = any(marker in response_text.lower() for marker in [
        '<!doctype html>', '<html', '<body', '<div', '<p>', '<h1>', '<style'
    ])
    
    # If it's not HTML content, return as a simple message
    if not has_html:
        return {
            "type": "text",
            "content": response_text,
            "status": "success"
        }

    # If response doesn't include HTML structure, wrap it in a default template
    if not ('<!DOCTYPE html>' in response_text or '<html' in response_text):
        default_style = """
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px; }
            h1, h2 { color: #333; }
            p { margin-bottom: 1em; color: #666; }
            .container { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            @media (max-width: 600px) {
                body { padding: 10px; }
                .container { padding: 15px; }
            }
        </style>
        """
        response_text = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            {default_style}
        </head>
        <body>
            <div class="container">
                {response_text}
            </div>
        </body>
        </html>
        """
    
    # Return a structured response for HTML content
    return {
        "type": "email_template",
        "content": {
            "message": "∘",
            "html": response_text
        },
        "status": "success"
    }

@app.post("/chat-sessions")
async def create_chat_session(session_data: ChatSessionCreate):
    """Create a new chat session"""
    db = SessionLocal()
    try:
        session = ChatSession(
            name=session_data.name,
            email_type=session_data.email_type
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return {
            "id": session.id,
            "name": session.name,
            "email_type": session.email_type,
            "created_at": session.created_at
        }
    finally:
        db.close()

@app.get("/chat-sessions")
async def list_chat_sessions():
    """List all chat sessions"""
    db = SessionLocal()
    try:
        sessions = db.query(ChatSession).all()
        return [{
            "id": session.id,
            "name": session.name,
            "email_type": session.email_type,
            "created_at": session.created_at,
            "message_count": len(session.messages)
        } for session in sessions]
    finally:
        db.close()

@app.get("/chat-sessions/{session_id}/messages")
async def get_chat_messages(session_id: int):
    """Get all messages for a chat session"""
    db = SessionLocal()
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        return [{
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp
        } for msg in session.messages]
    finally:
        db.close()

@app.delete("/chat-sessions/{session_id}")
async def delete_chat_session(session_id: int):
    """Delete a chat session and all its messages"""
    db = SessionLocal()
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        db.delete(session)
        db.commit()
        return {"status": "success", "message": "Chat session deleted"}
    finally:
        db.close()

@app.post("/ai/chat")
async def chat_with_ai(request: ChatRequest):
    """Handle chat requests and maintain conversation context."""
    
    db = SessionLocal()
    try:
        formatted_prompt = request.prompt
        conversation_context = []
        
        if request.session_id:
            messages = (
                db.query(ChatMessage)
                .filter(ChatMessage.session_id == request.session_id)
                .order_by(ChatMessage.timestamp.desc())
                .limit(10)
                .all()
            )
            conversation_context = [{"role": msg.role, "content": msg.content} for msg in reversed(messages)]
        
        try:
            system_prompt = request.system_prompt or DEFAULT_SYSTEM_PROMPT
            
            response = requests.post(
                OLLAMA_API,
                json={
                    "model": "deepseek-coder:6.7b",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        *conversation_context,
                        {"role": "user", "content": formatted_prompt}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_ctx": 4096
                    }
                }
            )
            
            if response.status_code != 200:
                error_message = handle_ollama_error(response.text)
                logger.error(f"Ollama API error: {response.text}")
                return {
                    "response": error_message,
                    "status": "error"
                }
            
            response_data = response.json()
            response_text = response_data.get("message", {}).get("content", "").strip()
            
            if not response_text:
                return {
                    "response": "I apologize, but I didn't receive a proper response. Please try again.",
                    "status": "error"
                }
            
            # Format the response
            formatted_response = format_chat_response(response_text, request.email_type)
            
            # Save to database if we have a session
            if request.session_id:
                # Save the display message, not the raw HTML
                display_content = (
                    formatted_response["content"]["message"] 
                    if formatted_response["type"] == "email_template"
                    else formatted_response["content"]
                )
                
                new_message = ChatMessage(
                    session_id=request.session_id,
                    role="assistant",
                    content=display_content,
                )
                
                db.add(new_message)
                db.commit()
            
            return formatted_response
        except Exception as e:
            logger.error(f"Error in chat_with_ai: {str(e)}")
            return {
                "response": "An error occurred while processing your request. Please try again.",
                "status": "error"
            }
    finally:
        db.close()

@app.post("/ai/generate-newsletter")
async def generate_newsletter(request: NewsletterRequest):
    try:
        prompt = f"""Generate an HTML newsletter about {request.topic}.
Content details: {json.dumps(request.content_details)}
Style preferences: {json.dumps(request.style_preferences) if request.style_preferences else 'None'}

Please generate a complete, well-formatted HTML newsletter that can be used directly."""

        response = requests.post(
            OLLAMA_API,
            json={
                "model": "deepseek-coder:6.7b",
                "system": DEFAULT_SYSTEM_PROMPT,
                "prompt": prompt,
                "format": "json",
                "options": {
                    "temperature": 0.7,
                    "num_ctx": 4096
                }
            }
        )
        
        if response.status_code != 200:
            print(f"Ollama API error: {response.text}")
            raise HTTPException(status_code=500, detail=f"Failed to generate newsletter: {response.text}")
        
        response_data = response.json()
        newsletter_html = response_data.get("response", "").strip()
        
        if not newsletter_html:
            raise HTTPException(status_code=500, detail="Failed to generate newsletter content")
        
        return {
            "html": newsletter_html,
            "status": "success"
        }
    except Exception as e:
        print(f"Error in generate_newsletter: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/quota")
async def get_quota():
    # For local development, we can return unlimited quota
    return {
        "remaining_chats": 999,
        "max_chats": 999,
        "remaining_emails": 999,
        "max_emails": 999
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 