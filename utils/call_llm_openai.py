import os
import logging
import json
from datetime import datetime
from openai import OpenAI

# Configure logging
log_directory = os.getenv("LOG_DIR", "logs")
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(
    log_directory, f"llm_calls_{datetime.now().strftime('%Y%m%d')}.log"
)

# Set up logger
logger = logging.getLogger("llm_logger")
logger.setLevel(logging.INFO)
logger.propagate = False  # Prevent propagation to root logger
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)

# Simple cache configuration
cache_file = "llm_cache.json"

def call_llm(prompt: str, use_cache: bool = True) -> str:
    # Log the prompt
    logger.info(f"PROMPT: {prompt}")

    # Check cache if enabled
    if use_cache:
        # Load cache from disk
        cache = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")

        # Return from cache if exists
        if prompt in cache:
            logger.info(f"CACHED RESPONSE: {cache[prompt]}")
            return cache[prompt]

    # Initialize OpenAI client
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    try:
        response = client.chat.completions.create(
            model="o1",  # Update to latest model
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_tokens=1000,  # Adjust as needed
            temperature=0.7  # Add common parameters
        )
        
        response_text = response.choices[0].message.content

        # Log the response
        logger.info(f"RESPONSE: {response_text}")

        # Update cache if enabled
        if use_cache:
            cache[prompt] = response_text
            try:
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(cache, f)
            except Exception as e:
                logger.error(f"Failed to save cache: {e}")

        return response_text

    except Exception as e:
        logger.error(f"API call failed: {e}")
        raise

if __name__ == "__main__":
    test_prompt = "Hello, how are you?"
    
    # First call - should hit the API
    print("Making call...")
    response1 = call_llm(test_prompt, use_cache=False)
    print(f"Response: {response1}")

    # Second call - should use cache if enabled
    print("Making cached call...")
    response2 = call_llm(test_prompt)
    print(f"Cached Response: {response2}")