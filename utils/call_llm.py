from google import genai
import os
import logging
import json
from datetime import datetime

# Configure logging
log_directory = os.getenv("LOG_DIR", "logs")
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(log_directory, f"llm_calls_{datetime.now().strftime('%Y%m%d')}.log")

# Set up logger
logger = logging.getLogger("llm_logger")
logger.setLevel(logging.INFO)
logger.propagate = False  # Prevent propagation to root logger
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Cache configuration from environment variables
cache_file = os.getenv("CACHE_FILE", "llm_cache.json")
cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"

# By default, we use Google Gemini 2.5 pro, as it shows great performance for code understanding
def call_llm(prompt: str, use_cache: bool = None) -> str:
    # Determine if cache should be used (parameter overrides environment variable)
    if use_cache is None:
        use_cache = cache_enabled
    
    # Log the prompt
    logger.info(f"PROMPT: {prompt}")
    
    # Check cache if enabled
    if use_cache:
        # Load cache from disk
        cache = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cache = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache, starting with empty cache: {e}")
        
        # Return from cache if exists
        if prompt in cache:
            logger.info(f"RESPONSE (cached): {cache[prompt]}")
            return cache[prompt]
    
    # Call the LLM if not in cache or cache disabled
    try:
        # Check if using API key or Vertex AI
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            # Use API key authentication
            client = genai.Client(api_key=api_key)
        else:
            # Use Vertex AI authentication
            client = genai.Client(
                vertexai=True,
                project=os.getenv("GEMINI_PROJECT_ID", "your-project-id"),
                location=os.getenv("GEMINI_LOCATION", "us-central1")
            )
            
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro-exp-03-25")
        response = client.models.generate_content(
            model=model,
            contents=[prompt]
        )
        response_text = response.text
        
        # Log the response
        logger.info(f"RESPONSE: {response_text}")
        
        # Update cache if enabled
        if use_cache:
            # Load cache again to avoid overwrites
            cache = {}
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r') as f:
                        cache = json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to reload cache: {e}")
            
            # Add to cache and save
            cache[prompt] = response_text
            try:
                with open(cache_file, 'w') as f:
                    json.dump(cache, f)
            except Exception as e:
                logger.error(f"Failed to save cache: {e}")
        
        return response_text
    
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        raise Exception(f"Failed to generate content with Gemini: {e}")

# # Use Anthropic Claude 3.7 Sonnet Extended Thinking
# def call_llm(prompt, use_cache: bool = True):
#     from anthropic import Anthropic
#     client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "your-api-key"))
#     response = client.messages.create(
#         model="claude-3-7-sonnet-20250219",
#         max_tokens=21000,
#         thinking={
#             "type": "enabled",
#             "budget_tokens": 20000
#         },
#         messages=[
#             {"role": "user", "content": prompt}
#         ]
#     )
#     return response.content[1].text

# # Use OpenAI o1
# def call_llm(prompt, use_cache: bool = True):    
#     from openai import OpenAI
#     client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
#     r = client.chat.completions.create(
#         model="o1",
#         messages=[{"role": "user", "content": prompt}],
#         response_format={
#             "type": "text"
#         },
#         reasoning_effort="medium",
#         store=False
#     )
#     return r.choices[0].message.content

if __name__ == "__main__":
    test_prompt = "Hello, how are you?"
    
    # First call - should hit the API
    print("Making call...")
    response1 = call_llm(test_prompt, use_cache=False)
    print(f"Response: {response1}")
    
