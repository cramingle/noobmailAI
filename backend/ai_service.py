import anthropic
import os
import openai
import requests
from typing import List, Dict, Any, Optional
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API keys from environment variables
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
XAI_API_KEY = os.environ.get("XAI_API_KEY", "")

# Debug logging
logger.info(f"ANTHROPIC_API_KEY present: {bool(ANTHROPIC_API_KEY)}")
logger.info(f"OPENAI_API_KEY present: {bool(OPENAI_API_KEY)}")
logger.info(f"XAI_API_KEY present: {bool(XAI_API_KEY)}")

class AIService:
    def __init__(self, anthropic_api_key: Optional[str] = None, openai_api_key: Optional[str] = None, xai_api_key: Optional[str] = None):
        """Initialize the AI service with API keys for Anthropic, OpenAI, and X.AI."""
        self.anthropic_api_key = anthropic_api_key or ANTHROPIC_API_KEY
        self.openai_api_key = openai_api_key or OPENAI_API_KEY
        self.xai_api_key = xai_api_key or XAI_API_KEY
        
        # Debug logging
        logger.info(f"AIService init - Anthropic API key present: {bool(self.anthropic_api_key)}")
        logger.info(f"AIService init - OpenAI API key present: {bool(self.openai_api_key)}")
        logger.info(f"AIService init - X.AI API key present: {bool(self.xai_api_key)}")
        
        # Initialize clients based on available API keys
        self.anthropic_client = None
        self.openai_client = None
        self.preferred_provider = None
        
        # Validate API keys by making a small test request
        if self.xai_api_key:
            try:
                # Test with a minimal request to validate the X.AI API key
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.xai_api_key}"
                }
                data = {
                    "messages": [{"role": "user", "content": "Hello"}],
                    "model": "grok-2-latest",
                    "stream": False,
                    "temperature": 0
                }
                response = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                if response.status_code == 200:
                    self.preferred_provider = "xai"
                    logger.info("X.AI API key validated successfully")
                else:
                    logger.error(f"X.AI API key validation failed: {response.text}")
            except Exception as e:
                logger.error(f"Failed to initialize X.AI API: {str(e)}")

        if not self.preferred_provider and self.anthropic_api_key:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
                # Test with a minimal request to validate the API key
                try:
                    self.anthropic_client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=10,
                        messages=[
                            {"role": "user", "content": "Hello"}
                        ]
                    )
                    self.preferred_provider = "anthropic"
                    logger.info("Anthropic API key validated successfully")
                except Exception as e:
                    logger.error(f"Anthropic API key validation failed: {str(e)}")
                    self.anthropic_client = None
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic API: {str(e)}")
                self.anthropic_client = None
        
        if not self.preferred_provider and self.openai_api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
                # Test with a minimal request to validate the API key
                try:
                    self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        max_tokens=10,
                        messages=[
                            {"role": "user", "content": "Hello"}
                        ]
                    )
                    self.preferred_provider = "openai"
                    logger.info("OpenAI API key validated successfully")
                except Exception as e:
                    logger.error(f"OpenAI API key validation failed: {str(e)}")
                    self.openai_client = None
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI API: {str(e)}")
                self.openai_client = None
        
        if not self.preferred_provider:
            logger.warning("No valid API keys provided. AI features will be simulated.")
        else:
            logger.info(f"Using {self.preferred_provider} as the preferred AI provider")
        
        # Model configuration
        self.anthropic_model = "claude-3-opus-20240229"
        self.openai_model = "gpt-4-turbo-preview"
        self.xai_model = "grok-2-latest"
        self.max_tokens = 4000
        self.temperature = 0.7
        
        # Track usage for quota management
        self.chat_count = 0
        self.max_chat_count = 10  # Default limit
        
    def generate_response(self, 
                          prompt: str, 
                          context: Optional[List[Dict[str, str]]] = None,
                          system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a response from the AI model.
        
        Args:
            prompt: The user's input prompt
            context: Optional list of previous messages for context
            system_prompt: Optional system prompt to guide the AI
            
        Returns:
            Dictionary containing the AI response and metadata
        """
        try:
            # Check if user has exceeded chat quota
            if self.chat_count >= self.max_chat_count:
                return {
                    "success": False,
                    "error": "Chat quota exceeded",
                    "message": "You've reached your chat limit. Please join our waitlist for continued access."
                }
            
            # Increment chat count
            self.chat_count += 1
            
            # Log the current state
            logger.info(f"Generating response with provider: {self.preferred_provider}")
            
            # If no API clients are available, provide a simulated response
            if not self.preferred_provider:
                return {
                    "success": True,
                    "message": f"I would help you create a newsletter about '{prompt}', but I'm currently in demo mode without an API key. Please add your API key to use the full AI features.",
                    "remaining_chats": self.max_chat_count - self.chat_count
                }
            
            # Default system prompt for newsletter generation if none provided
            default_system_prompt = "You are an expert newsletter writer and designer. Help the user create engaging, professional newsletters. When asked to generate newsletter content, provide well-structured HTML that can be directly used in an email campaign. Focus on creating content that is visually appealing, mobile-responsive, and follows email marketing best practices."
            
            # Try X.AI first if it's the preferred provider
            if self.preferred_provider == "xai":
                try:
                    # Prepare messages for X.AI
                    messages = []
                    
                    # Add system prompt
                    if system_prompt or default_system_prompt:
                        messages.append({
                            "role": "system",
                            "content": system_prompt or default_system_prompt
                        })
                    
                    # Add conversation context if provided
                    if context:
                        messages.extend(context)
                    
                    # Add the current user prompt
                    messages.append({"role": "user", "content": prompt})
                    
                    # Call the X.AI API
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.xai_api_key}"
                    }
                    data = {
                        "messages": messages,
                        "model": self.xai_model,
                        "stream": False,
                        "temperature": self.temperature
                    }
                    response = requests.post(
                        "https://api.x.ai/v1/chat/completions",
                        headers=headers,
                        json=data
                    )
                    response_data = response.json()
                    
                    return {
                        "success": True,
                        "message": response_data["choices"][0]["message"]["content"],
                        "remaining_chats": self.max_chat_count - self.chat_count,
                        "provider": "xai",
                        "usage": response_data.get("usage", {})
                    }
                except Exception as e:
                    logger.error(f"X.AI API error: {str(e)}")
                    # If X.AI fails and another provider is available, fall back
                    if self.anthropic_client:
                        logger.info("Falling back to Anthropic API")
                        self.preferred_provider = "anthropic"
                    elif self.openai_client:
                        logger.info("Falling back to OpenAI API")
                        self.preferred_provider = "openai"
                    else:
                        raise e

            # Try Anthropic if it's preferred or if X.AI failed
            if self.preferred_provider == "anthropic" and self.anthropic_client:
                try:
                    # Prepare messages for Anthropic
                    messages = []
                    
                    # Add system prompt
                    messages.append({
                        "role": "system", 
                        "content": system_prompt or default_system_prompt
                    })
                    
                    # Add conversation context if provided
                    if context:
                        messages.extend(context)
                        
                    # Add the current user prompt
                    messages.append({"role": "user", "content": prompt})
                    
                    # Call the Anthropic API
                    response = self.anthropic_client.messages.create(
                        model=self.anthropic_model,
                        messages=messages,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature
                    )
                    
                    # Extract and return the response
                    return {
                        "success": True,
                        "message": response.content[0].text,
                        "remaining_chats": self.max_chat_count - self.chat_count,
                        "provider": "anthropic",
                        "usage": {
                            "input_tokens": response.usage.input_tokens,
                            "output_tokens": response.usage.output_tokens
                        }
                    }
                except Exception as e:
                    logger.error(f"Anthropic API error: {str(e)}")
                    # If Anthropic fails and OpenAI is available, fall back to OpenAI
                    if self.openai_client:
                        logger.info("Falling back to OpenAI API")
                        self.preferred_provider = "openai"
                    else:
                        raise e
            
            # Use OpenAI if it's preferred or if Anthropic failed
            if self.preferred_provider == "openai" and self.openai_client:
                # Prepare messages for OpenAI
                messages = []
                
                # Add system prompt
                messages.append({
                    "role": "system", 
                    "content": system_prompt or default_system_prompt
                })
                
                # Add conversation context if provided
                if context:
                    for msg in context:
                        messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
                
                # Add the current user prompt
                messages.append({"role": "user", "content": prompt})
                
                # Call the OpenAI API
                response = self.openai_client.chat.completions.create(
                    model=self.openai_model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                
                # Extract and return the response
                return {
                    "success": True,
                    "message": response.choices[0].message.content,
                    "remaining_chats": self.max_chat_count - self.chat_count,
                    "provider": "openai",
                    "usage": {
                        "total_tokens": response.usage.total_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "prompt_tokens": response.usage.prompt_tokens
                    }
                }
            
            # If we get here, both APIs failed
            raise Exception("All AI providers failed to generate a response")
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"An error occurred while generating the AI response: {str(e)}. Please check your API keys in the .env file or try again later."
            }
    
    def generate_newsletter_html(self, 
                               topic: str, 
                               content_details: Dict[str, Any],
                               style_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a complete newsletter HTML based on the provided topic and content details.
        
        Args:
            topic: The main topic or subject of the newsletter
            content_details: Details about the content to include
            style_preferences: Optional styling preferences
            
        Returns:
            Dictionary containing the generated HTML and metadata
        """
        # Create a detailed prompt for newsletter generation
        prompt = f"""
        Create a complete HTML newsletter on the topic: {topic}
        
        Content details:
        - Main headline: {content_details.get('headline', 'Newsletter')}
        - Sections: {', '.join(content_details.get('sections', []))}
        - Call to action: {content_details.get('cta', 'Subscribe for more')}
        
        Style preferences:
        """
        
        if style_preferences:
            prompt += f"""
            - Color scheme: {style_preferences.get('colors', 'Professional')}
            - Layout: {style_preferences.get('layout', 'Single column')}
            - Image placement: {style_preferences.get('images', 'Top of sections')}
            """
        
        prompt += """
        Please provide the complete HTML code for this newsletter, ensuring it is:
        1. Mobile-responsive
        2. Well-structured with proper HTML tags
        3. Ready to be used in an email campaign
        4. Includes placeholder text for all sections
        5. Has a clean, professional design
        
        Return ONLY the HTML code without any explanations.
        """
        
        system_prompt = """
        You are an expert newsletter designer. Your task is to create complete, ready-to-use HTML email templates.
        
        Follow these guidelines:
        - Use table-based layouts for maximum email client compatibility
        - Include inline CSS for styling
        - Create mobile-responsive designs
        - Use placeholder text that matches the requested content
        - Follow email marketing best practices
        - Return ONLY the HTML code without explanations or markdown formatting
        """
        
        # Generate the newsletter HTML
        response = self.generate_response(prompt, system_prompt=system_prompt)
        
        # If successful, extract just the HTML code
        if response["success"]:
            # Clean up the response to extract just the HTML
            html_content = response["message"]
            
            # Remove any markdown code block formatting if present
            if "```html" in html_content:
                html_content = html_content.split("```html")[1].split("```")[0].strip()
            elif "```" in html_content:
                html_content = html_content.split("```")[1].split("```")[0].strip()
                
            response["html_content"] = html_content
            
        return response
    
    def reset_chat_count(self):
        """Reset the chat count for the user."""
        self.chat_count = 0
        
    def set_max_chat_count(self, count: int):
        """Set the maximum number of chats allowed."""
        self.max_chat_count = count

# Create a singleton instance
ai_service = AIService() 