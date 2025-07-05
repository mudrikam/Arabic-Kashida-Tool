import google.generativeai as genai
import os
import json

def configure_gemini_api():
    """Configure the Gemini API with your API key."""
    # Try environment variable first
    api_key = os.getenv("GEMINI_API_KEY")
    
    # If not found, try config file
    if not api_key:
        try:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
            with open(config_path, 'r') as f:
                config = json.load(f)
                api_key = config.get("gemini", {}).get("api_key")
        except:
            pass
    
    # If still not found, ask user to set it
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Please set it in environment variable or config.json")
    
    genai.configure(api_key=api_key)

def request_gemini(prompt):
    """
    Send a prompt to Gemini and return the plain text response.
    """
    try:
        configure_gemini_api()
        
        # Create the model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Generate content
        response = model.generate_content(prompt)
        
        # Extract text from response
        if hasattr(response, 'text'):
            return response.text
        elif hasattr(response, 'parts') and response.parts:
            return response.parts[0].text
        else:
            return str(response)
            
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")