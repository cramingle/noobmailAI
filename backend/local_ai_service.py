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
env_file = os.getenv('ENV_FILE', '.env')
load_dotenv(env_file)
logger = logging.getLogger(__name__)
logger.info(f"Loading environment from: {env_file}")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Ollama API Configuration
OLLAMA_API = os.getenv('OLLAMA_API_URL', 'http://localhost:11434/api/chat')
DEFAULT_SYSTEM_PROMPT = """You are Boon, an AI email styling expert who helps people create beautifully designed emails that make great first impressions. Your personality is friendly and conversational, but also professional.

Follow these principles:
1. Start with conversation - understand the user's needs before creating anything
2. Keep initial responses brief and friendly
3. When user asks to "create email" or any variation of that:
   - If they provide specific requirements, use those
   - If they say "dummy" or "anything", create a modern product announcement email
   - ALWAYS respond with complete HTML and CSS, wrapped in ```html tags
4. NEVER just write plain text emails - always use HTML and CSS
5. For styling, always include:
   - Responsive design (mobile-first)
   - Modern color schemes
   - Professional typography
   - Proper spacing and padding
   - Clear visual hierarchy
   - Email client compatibility

Example response format when asked to create an email:
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Email</title>
    <style>
        /* Your CSS here */
    </style>
</head>
<body>
    <!-- Your email content here -->
</body>
</html>
```

Remember: 
1. Be conversational for general chat
2. When asked to create an email, ALWAYS provide complete HTML/CSS
3. Focus on modern, responsive design that works across email clients."""

# Get allowed origins from environment variable or use default
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS")
if not ALLOWED_ORIGINS:
    logger.warning("ALLOWED_ORIGINS not set in environment, using default values")
    ALLOWED_ORIGINS = "http://localhost:5173,http://localhost:3000,https://noobmail.zirodelta.com"

logger.info(f"Configured ALLOWED_ORIGINS: {ALLOWED_ORIGINS}")
ALLOWED_ORIGINS = ALLOWED_ORIGINS.split(",")

app = FastAPI()

# Create database session
SessionLocal = sessionmaker(bind=engine)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Authorization"]
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
    email_type: Optional[str] = "professional"  # Can be "professional" or "career"

class ChatSessionCreate(BaseModel):
    name: str
    email_type: str = "professional"

class NewsletterRequest(BaseModel):
    topic: str
    content_details: Dict[str, Any]
    style_preferences: Optional[Dict[str, Any]] = None

def validate_email_request(prompt: str, email_type: str = "professional") -> bool:
    """Validate if the request is related to email creation."""
    email_keywords = {
        "professional": [
            'newsletter', 'email', 'template', 'campaign',
            'header', 'footer', 'design', 'layout',
            'responsive', 'html', 'subject line', 'edm',
            'marketing email', 'email blast', 'mailing list',
            'scholarship', 'academic', 'application letter',
            'statement of purpose', 'motivation letter',
            'research proposal', 'grant application',
            'funding request', 'academic achievement',
            'educational background', 'study plan'
        ],
        "career": [
            'job application', 'cover letter', 'job email',
            'application email', 'resume', 'cv', 'hiring manager',
            'recruiter', 'position', 'job opening', 'vacancy',
            'career', 'opportunity', 'employment', 'apply',
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

def enforce_anti_spam_elements(html: str, email_type: str = "professional") -> str:
    """Ensure HTML includes all necessary anti-spam elements based on email type."""
    required_elements = {
        'viewport': '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        'content_type': '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
    }
    
    if email_type == "professional":
        required_elements.update({
            'unsubscribe': '<a href="{unsubscribe_url}" style="color: #666666; text-decoration: underline;">Unsubscribe</a>',
            'physical_address': '<p style="color: #666666; font-size: 12px;">{company_address}</p>',
            'permission_reminder': '<p style="color: #666666; font-size: 12px;">You received this email because you signed up for updates from {company_name}.</p>'
        })
    else:  # career
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

def format_chat_response(response_text: str, email_type: str = "professional") -> Dict[str, Any]:
    """Format the chat response, handling HTML content specially."""
    # Check if the response contains HTML-like content
    has_html = any(marker in response_text.lower() for marker in [
        '<!doctype html>', '<html', '<body', '<div', '<p>', '<h1>', '<style'
    ])
    
    # If it's not HTML content, return as a simple text message
    if not has_html:
        return {
            "type": "text",
            "content": response_text,
            "status": "success"
        }

    # Extract the conversational message and HTML content
    parts = response_text.split("```html")
    message = parts[0].strip() if len(parts) > 1 else "Here's your professionally designed email template:"
    html_content = parts[1].split("```")[0].strip() if len(parts) > 1 else response_text

    # Return the structured response
    return {
        "type": "email_template",
        "content": {
            "message": message,
            "html": html_content
        },
        "status": "success"
    }

@app.post("/chat-sessions")
async def create_chat_session(session_data: ChatSessionCreate):
    """Create a new chat session."""
    try:
        db = SessionLocal()
        session = ChatSession(
            name=session_data.name,
            email_type=session_data.email_type
        )
        db.add(session)
        db.commit()
        return {"id": session.id, "name": session.name}
    except Exception as e:
        logger.error(f"Error creating chat session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create chat session")
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
    """Handle chat requests with AI."""
    try:
        # Initialize messages with system prompt
        messages = [
            {
                "role": "system",
                "content": request.system_prompt or DEFAULT_SYSTEM_PROMPT
            }
        ]
        
        # Get existing conversation from database if session_id is provided
        db = SessionLocal()
        try:
            if not request.session_id:
                # Create a new session if none provided
                session = ChatSession(
                    name=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    email_type=request.email_type or "professional"
                )
                db.add(session)
                db.commit()
                request.session_id = session.id
            
            # Get existing messages for the session
            existing_messages = (
                db.query(ChatMessage)
                .filter(ChatMessage.session_id == request.session_id)
                .order_by(ChatMessage.timestamp)
                .all()
            )
            
            # Add existing conversation to messages
            for msg in existing_messages:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Add current context if provided (overrides database context)
            if request.context:
                messages.extend([{
                    "role": msg.role,
                    "content": msg.content
                } for msg in request.context])
            
            # Add the current prompt
            current_message = {
                "role": "user",
                "content": request.prompt
            }
            messages.append(current_message)
            
            # Store user message immediately
            user_message = ChatMessage(
                session_id=request.session_id,
                role="user",
                content=request.prompt,
                timestamp=datetime.now()
            )
            db.add(user_message)
            db.commit()
            
            # Make request to Ollama API
            try:
                logger.info(f"Sending request to Ollama API with {len(messages)} messages in context")
                logger.info(f"Request payload: {json.dumps({'model': 'mistral', 'messages': messages})}")
                
                response = requests.post(
                    OLLAMA_API,
                    json={
                        "model": "mistral",
                        "messages": messages,
                        "stream": False
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Ollama API error: {response.text}")
                    raise HTTPException(status_code=500, detail="Failed to get response from AI")
                
                response_data = response.json()
                response_text = response_data.get("message", {}).get("content", "")
                
                if not response_text:
                    logger.error("Empty response from AI")
                    raise HTTPException(status_code=500, detail="Empty response from AI")
                
                # Store AI response
                ai_message = ChatMessage(
                    session_id=request.session_id,
                    role="assistant",
                    content=response_text,
                    timestamp=datetime.now()
                )
                db.add(ai_message)
                db.commit()
                
                # Format the response based on content type
                formatted_response = format_chat_response(response_text, request.email_type)
                
                # Include session_id in response
                formatted_response["session_id"] = request.session_id
                return formatted_response
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error calling Ollama API: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to communicate with AI service")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
                "model": "mistral",
                "prompt": f"{DEFAULT_SYSTEM_PROMPT}\n\n{prompt}",
                "stream": False
            }
        )
        
        if response.status_code != 200:
            logger.error(f"Ollama API error: {response.text}")
            raise HTTPException(status_code=500, detail=f"Failed to generate newsletter: {response.text}")
        
        response_data = response.json()
        newsletter_html = response_data.get("response", "").strip()
        
        if not newsletter_html:
            raise HTTPException(status_code=500, detail="Failed to generate newsletter content")
        
        # Clean and format the HTML
        if not newsletter_html.startswith('<!DOCTYPE html>'):
            newsletter_html = f'<!DOCTYPE html>\n{newsletter_html}'
        
        newsletter_html = enforce_anti_spam_elements(newsletter_html)
        newsletter_html = optimize_for_spam_filters(newsletter_html)
        
        return {
            "html": newsletter_html,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error in generate_newsletter: {str(e)}")
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