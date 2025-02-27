from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import requests
import json
import re
from datetime import datetime
from sqlalchemy.orm import Session, sessionmaker
from models import ChatSession, ChatMessage, engine
import logging
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

OLLAMA_API = "http://localhost:11434/api/chat"

# Default system prompt for newsletter creation
DEFAULT_SYSTEM_PROMPT = """You are Boon, the AI assistant for NoobMail. Your name "Boon" represents the opposite of "noob" because you help users become email experts. You are friendly, professional, and focused specifically on helping users create amazing emails and newsletters.

YOUR IDENTITY:
1. You are Boon, NoobMail's dedicated email assistant
2. Your purpose is to help users create professional and effective emails
3. You focus exclusively on email-related tasks and questions
4. You don't handle programming or technical questions outside of email creation
5. You're proud to help users transform from email "noobs" to "boons"

COMMUNICATION STYLE:
1. Warm and encouraging
2. Professional but approachable
3. Focus on email best practices
4. Guide users step by step
5. Use clear, non-technical language
6. Always stay focused on email-related topics

WHEN HELPING WITH EMAILS:

FOR NEWSLETTERS:
1. First, ask about:
   - The main topic or purpose
   - Target audience
   - Key message they want to convey
   - Any specific preferences for style

2. Then guide them through content:
   - Suggest engaging subject lines
   - Help structure the main message
   - Recommend layout ideas
   - Offer example templates

3. Only after understanding their needs, create:
   - Professional, clean design
   - Mobile-friendly layout
   - Spam-safe content
   - Easy-to-read structure

FOR JOB APPLICATIONS:
1. First, ask about:
   - The specific role
   - Company details
   - Their key qualifications
   - Any specific requirements

2. Then help them:
   - Craft attention-grabbing openings
   - Highlight relevant experience
   - Structure their qualifications
   - Create compelling call-to-action

3. Only after understanding their needs, create:
   - Professional formatting
   - ATS-friendly structure
   - Clear contact information
   - Impactful closing

TECHNICAL REQUIREMENTS (Handle these automatically without technical discussion):
1. Email Best Practices:
   - Clean HTML structure
   - Mobile responsiveness
   - Spam filter compliance
   - Email client compatibility

2. Content Optimization:
   - Professional formatting
   - Proper spacing
   - Clear hierarchy
   - Balanced layout

Remember: Users don't need to know about HTML, CSS, or technical details. Focus on their content and goals, and handle the technical implementation invisibly. Stay focused on email creation and avoid discussing technical implementation details. If users ask about programming or non-email topics, politely remind them that you're specialized in email creation and guide them back to email-related discussions.

When users ask for help:
1. Start with questions about their needs
2. Offer suggestions and examples
3. Guide them through choices
4. Generate the email only after understanding their requirements
5. Always explain next steps clearly

Keep the conversation natural and focused on their goals, not the technical implementation."""

def validate_email_request(prompt: str, email_type: str = "newsletter") -> bool:
    """Validate if the request is related to email creation."""
    newsletter_keywords = [
        'newsletter', 'email', 'template', 'campaign',
        'header', 'footer', 'design', 'layout',
        'responsive', 'html', 'subject line', 'edm',
        'marketing email', 'email blast', 'mailing list'
    ]
    
    job_application_keywords = [
        'job application', 'cover letter', 'job email',
        'application email', 'resume', 'cv', 'hiring manager',
        'recruiter', 'position', 'job opening', 'vacancy',
        'career', 'opportunity', 'employment', 'apply'
    ]
    
    if email_type == "newsletter":
        return any(keyword in prompt.lower() for keyword in newsletter_keywords)
    elif email_type == "job_application":
        return any(keyword in prompt.lower() for keyword in job_application_keywords)
    else:
        # If type not specified, check for either
        return any(keyword in prompt.lower() for keyword in newsletter_keywords + job_application_keywords)

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
    
    # Get database session
    db = SessionLocal()
    try:
        # Determine if this is a request for HTML generation
        is_html_request = validate_email_request(request.prompt, request.email_type)
        
        # Format the prompt based on the type of request
        formatted_prompt = request.prompt
        if is_html_request:
            formatted_prompt = f"""Please create an HTML email template for a {request.email_type}.
Requirements:
- Professional structure
- Clean HTML format
- Include subject line, greeting, body, and signature
- Focus on: {request.prompt}

Technical requirements:
- Use semantic HTML5
- Include proper meta tags
- Ensure mobile responsiveness
- Keep styling minimal and professional

Please output the HTML template:"""
        
        # Get conversation context if session exists
        conversation_context = []
        if request.session_id:
            # Get last 10 messages from the session
            messages = (
                db.query(ChatMessage)
                .filter(ChatMessage.session_id == request.session_id)
                .order_by(ChatMessage.timestamp.desc())
                .limit(10)
                .all()
            )
            conversation_context = [
                {"role": msg.role, "content": msg.content}
                for msg in reversed(messages)
            ]
        
        # Add any provided context
        if request.context:
            conversation_context.extend(request.context)
        
        try:
            # Call Ollama API with conversation context
            response = requests.post(
                OLLAMA_API,
                json={
                    "model": "deepseek-coder:6.7b",
                    "prompt": request.prompt,
                    "stream": True,
                    "context": conversation_context,
                    "system": request.system_prompt or DEFAULT_SYSTEM_PROMPT
                }
            )
            
            if response.status_code != 200:
                error_message = handle_ollama_error(response.text)
                print(f"Ollama API error: {response.text}")
                return {
                    "response": error_message,
                    "status": "error"
                }
            
            # Parse the streaming response
            response_text = ""
            for line in response.text.split('\n'):
                if line.strip():
                    try:
                        chunk = json.loads(line)
                        if "message" in chunk and "content" in chunk["message"]:
                            response_text += chunk["message"]["content"]
                    except json.JSONDecodeError:
                        continue
            
            response_text = response_text.strip()
            
            # If response contains HTML and this was a HTML request, optimize it
            if is_html_request and ('<html' in response_text or '<body' in response_text):
                response_text = optimize_for_spam_filters(response_text)
                response_text = enforce_anti_spam_elements(response_text, request.email_type)
            
            # Save messages to database if session exists
            if request.session_id:
                # Save user message
                user_message = ChatMessage(
                    session_id=request.session_id,
                    role="user",
                    content=request.prompt
                )
                db.add(user_message)
                
                # Save assistant message
                assistant_message = ChatMessage(
                    session_id=request.session_id,
                    role="assistant",
                    content=response_text
                )
                db.add(assistant_message)
                db.commit()
            
            return {
                "response": response_text,
                "status": "success"
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            return {
                "response": "I'm having trouble connecting to my language model. Please try again in a moment.",
                "status": "error"
            }
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return {
                "response": "An unexpected error occurred. Please try again.",
                "status": "error"
            }
    finally:
        db.close()

@app.post("/ai/generate-newsletter")
async def generate_newsletter(request: NewsletterRequest):
    try:
        response = requests.post(
            OLLAMA_API,
            json={
                "model": "deepseek-coder:6.7b",
                "messages": [
                    {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
                    {"role": "user", "content": f"""Generate an HTML newsletter about {request.topic}.
Content details: {json.dumps(request.content_details)}
Style preferences: {json.dumps(request.style_preferences) if request.style_preferences else 'None'}

Please generate a complete, well-formatted HTML newsletter that can be used directly."""}
                ],
                "stream": False
            }
        )
        
        if response.status_code != 200:
            print(f"Ollama API error: {response.text}")
            raise HTTPException(status_code=500, detail=f"Failed to generate newsletter: {response.text}")
        
        # Parse the streaming response
        newsletter_html = ""
        for line in response.text.split('\n'):
            if line.strip():
                try:
                    chunk = json.loads(line)
                    if "message" in chunk and "content" in chunk["message"]:
                        newsletter_html += chunk["message"]["content"]
                except json.JSONDecodeError:
                    continue
        
        return {
            "html": newsletter_html.strip(),
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