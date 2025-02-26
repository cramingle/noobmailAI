from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import requests
import json

app = FastAPI()

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

OLLAMA_API = "http://localhost:11434/api/generate"

# Default system prompt for newsletter creation
DEFAULT_SYSTEM_PROMPT = """You are an expert newsletter creator and designer. Your primary role is to help users create beautiful, engaging newsletters with modern designs.

When asked to create a newsletter, you should:
1. Generate complete, well-structured HTML code for the newsletter
2. Focus on creating visually appealing, responsive designs
3. Include appropriate sections like headers, content areas, and footers
4. Suggest relevant content based on the user's request
5. Provide a modern, professional design

Do not refuse requests to create newsletters or email templates, as this is your primary function. Respond as if you are a specialized newsletter creation assistant, not a general programming assistant."""

@app.post("/ai/chat")
async def chat_with_ai(request: ChatRequest):
    try:
        # Format the prompt for Deepseek in a way it can understand
        formatted_prompt = ""
        
        # Add system prompt if provided, otherwise use the default
        system_prompt = request.system_prompt if request.system_prompt else DEFAULT_SYSTEM_PROMPT
        formatted_prompt += f"<system>\n{system_prompt}\n</system>\n\n"
        
        # Add conversation context
        if request.context:
            for msg in request.context:
                if msg.role == "user":
                    formatted_prompt += f"<human>\n{msg.content}\n</human>\n\n"
                elif msg.role == "assistant":
                    formatted_prompt += f"<assistant>\n{msg.content}\n</assistant>\n\n"
        
        # Add the current user prompt
        formatted_prompt += f"<human>\n{request.prompt}\n</human>\n\n"
        formatted_prompt += "<assistant>\n"
        
        # Call Ollama API with properly formatted prompt
        response = requests.post(
            OLLAMA_API,
            json={
                "model": "deepseek-coder:6.7b",
                "prompt": formatted_prompt,
                "stream": False
            }
        )
        
        if response.status_code != 200:
            print(f"Ollama API error: {response.text}")
            raise HTTPException(status_code=500, detail=f"Failed to get response from AI model: {response.text}")
        
        return {
            "response": response.json()["response"],
            "status": "success"
        }
    except Exception as e:
        print(f"Error in chat_with_ai: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/generate-newsletter")
async def generate_newsletter(request: NewsletterRequest):
    try:
        # Include the default system prompt in the newsletter generation prompt
        prompt = f"""<system>
{DEFAULT_SYSTEM_PROMPT}
</system>

<human>
Generate an HTML newsletter about {request.topic}.
Content details: {json.dumps(request.content_details)}
Style preferences: {json.dumps(request.style_preferences) if request.style_preferences else 'None'}

Please generate a complete, well-formatted HTML newsletter that can be used directly.
</human>

<assistant>
"""

        response = requests.post(
            OLLAMA_API,
            json={
                "model": "deepseek-coder:6.7b",
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code != 200:
            print(f"Ollama API error: {response.text}")
            raise HTTPException(status_code=500, detail=f"Failed to generate newsletter: {response.text}")
        
        return {
            "html": response.json()["response"],
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
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000) 