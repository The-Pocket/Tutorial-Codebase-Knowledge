from google import genai
import os
import logging
import json
import sys
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

# Add console handler for errors
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logger.addHandler(console_handler)

# Simple cache configuration
cache_file = os.getenv("CACHE_FILE", "llm_cache.json")
use_cache_default = os.getenv("USE_CACHE", "true").lower() == "true"

# Validate environment variables function
def validate_env_for_provider(provider_name, required_vars):
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        logger.error(f"{provider_name} configuration incomplete. Missing: {', '.join(missing)}")
        return False
    return True

# By default, we use Google Gemini 2.5 pro, as it shows great performance for code understanding
def call_llm(prompt: str, use_cache: bool = use_cache_default) -> str:
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
                logger.warning(f"Failed to load cache: {e}. Starting with empty cache")
        
        # Return from cache if exists
        if prompt in cache:
            logger.info(f"CACHE HIT: Using cached response")
            return cache[prompt]
    
    try:
        # Determine which provider to use based on environment variables
        using_vertex = bool(os.getenv("GEMINI_PROJECT_ID"))
        using_ai_studio = bool(os.getenv("GEMINI_API_KEY"))
        
        # Call the LLM if not in cache or cache disabled
        if using_vertex:
            # Validate Vertex AI configuration
            if not validate_env_for_provider("Vertex AI", ["GEMINI_PROJECT_ID", "GEMINI_LOCATION"]):
                raise ValueError("Missing Vertex AI configuration. Set GEMINI_PROJECT_ID and GEMINI_LOCATION.")
                
            client = genai.Client(
                vertexai=True, 
                project=os.getenv("GEMINI_PROJECT_ID"),
                location=os.getenv("GEMINI_LOCATION", "us-central1")
            )
            logger.info("Using Vertex AI for Gemini")
        elif using_ai_studio:
            # Validate AI Studio configuration
            if not validate_env_for_provider("AI Studio", ["GEMINI_API_KEY"]):
                raise ValueError("Missing AI Studio configuration. Set GEMINI_API_KEY.")
                
            client = genai.Client(
                api_key=os.getenv("GEMINI_API_KEY"),
            )
            logger.info("Using AI Studio for Gemini")
        else:
            raise ValueError(
                "Google Gemini configuration not found. Please set either:\n"
                "1. GEMINI_PROJECT_ID and GEMINI_LOCATION for Vertex AI, or\n"
                "2. GEMINI_API_KEY for AI Studio\n"
                "See SETUP.md for detailed instructions."
            )
            
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro-exp-03-25")
        logger.info(f"Using model: {model}")
        
        response = client.models.generate_content(
            model=model,
            contents=[prompt]
        )
        response_text = response.text
        
        # Log the response
        logger.info(f"RESPONSE: {response_text[:200]}... (truncated)")
        
        # Update cache if enabled
        if use_cache:
            # Load cache again to avoid overwrites
            cache = {}
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r') as f:
                        cache = json.load(f)
                except:
                    pass
            
            # Add to cache and save
            cache[prompt] = response_text
            try:
                with open(cache_file, 'w') as f:
                    json.dump(cache, f)
            except Exception as e:
                logger.error(f"Failed to save cache: {e}")
        
        return response_text
        
    except Exception as e:
        logger.error(f"LLM call failed: {str(e)}")
        print(f"\nError calling LLM: {str(e)}")
        print("Please check your configuration and API keys. See SETUP.md for details.")
        raise

# # Use Anthropic Claude 3.7 Sonnet Extended Thinking
# def call_llm(prompt, use_cache: bool = use_cache_default):
#     try:
#         from anthropic import Anthropic
#         
#         # Validate configuration
#         if not validate_env_for_provider("Anthropic", ["ANTHROPIC_API_KEY"]):
#             raise ValueError("Missing Anthropic API key. Set ANTHROPIC_API_KEY environment variable.")
#             
#         logger.info("Using Anthropic Claude")
#         
#         # Check cache if enabled
#         if use_cache:
#             cache = {}
#             if os.path.exists(cache_file):
#                 try:
#                     with open(cache_file, 'r') as f:
#                         cache = json.load(f)
#                 except Exception as e:
#                     logger.warning(f"Failed to load cache: {e}")
#             
#             if prompt in cache:
#                 logger.info("CACHE HIT: Using cached response")
#                 return cache[prompt]
#         
#         client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
#         model = os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet-20250219")
#         logger.info(f"Using model: {model}")
#         
#         response = client.messages.create(
#             model=model,
#             max_tokens=21000,
#             thinking={
#                 "type": "enabled",
#                 "budget_tokens": 20000
#             },
#             messages=[
#                 {"role": "user", "content": prompt}
#             ]
#         )
#         response_text = response.content[1].text
#         
#         # Log and cache response
#         logger.info(f"RESPONSE: {response_text[:200]}... (truncated)")
#         if use_cache:
#             cache = {}
#             if os.path.exists(cache_file):
#                 try:
#                     with open(cache_file, 'r') as f:
#                         cache = json.load(f)
#                 except:
#                     pass
#             cache[prompt] = response_text
#             try:
#                 with open(cache_file, 'w') as f:
#                     json.dump(cache, f)
#             except Exception as e:
#                 logger.error(f"Failed to save cache: {e}")
#         
#         return response_text
#     except Exception as e:
#         logger.error(f"Anthropic LLM call failed: {str(e)}")
#         print(f"\nError calling Anthropic LLM: {str(e)}")
#         print("Please check your configuration and API key. See SETUP.md for details.")
#         raise

# # Use OpenAI O1
# def call_llm(prompt, use_cache: bool = use_cache_default):
#     try:
#         from openai import OpenAI
#         
#         # Validate configuration
#         if not validate_env_for_provider("OpenAI", ["OPENAI_API_KEY"]):
#             raise ValueError("Missing OpenAI API key. Set OPENAI_API_KEY environment variable.")
#             
#         logger.info("Using OpenAI")
#         
#         # Check cache if enabled
#         if use_cache:
#             cache = {}
#             if os.path.exists(cache_file):
#                 try:
#                     with open(cache_file, 'r') as f:
#                         cache = json.load(f)
#                 except Exception as e:
#                     logger.warning(f"Failed to load cache: {e}")
#             
#             if prompt in cache:
#                 logger.info("CACHE HIT: Using cached response")
#                 return cache[prompt]
#         
#         client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
#         model = os.getenv("OPENAI_MODEL", "o1")
#         logger.info(f"Using model: {model}")
#         
#         r = client.chat.completions.create(
#             model=model,
#             messages=[{"role": "user", "content": prompt}],
#             response_format={
#                 "type": "text"
#             },
#             reasoning_effort=os.getenv("OPENAI_REASONING", "medium"),
#             store=False
#         )
#         response_text = r.choices[0].message.content
#         
#         # Log and cache response
#         logger.info(f"RESPONSE: {response_text[:200]}... (truncated)")
#         if use_cache:
#             cache = {}
#             if os.path.exists(cache_file):
#                 try:
#                     with open(cache_file, 'r') as f:
#                         cache = json.load(f)
#                 except:
#                     pass
#             cache[prompt] = response_text
#             try:
#                 with open(cache_file, 'w') as f:
#                     json.dump(cache, f)
#             except Exception as e:
#                 logger.error(f"Failed to save cache: {e}")
#         
#         return response_text
#     except Exception as e:
#         logger.error(f"OpenAI LLM call failed: {str(e)}")
#         print(f"\nError calling OpenAI LLM: {str(e)}")
#         print("Please check your configuration and API key. See SETUP.md for details.")
#         raise

if __name__ == "__main__":
    test_prompt = "Hello, how are you?"
    
    try:
        # First call - should hit the API
        print("Testing LLM connection...")
        response = call_llm(test_prompt, use_cache=False)
        print(f"\n✅ LLM test successful! Response: {response[:100]}...")
        print("\nYour LLM setup is working correctly.")
    except Exception as e:
        print(f"\n❌ LLM test failed: {e}")
        print("\nPlease check your configuration and API keys.")
        print("See SETUP.md for detailed setup instructions.")
        sys.exit(1)

