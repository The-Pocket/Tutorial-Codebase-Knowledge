import os
import logging
import json
from datetime import datetime
from openai import OpenAI

# Configure logging
def setup_logger():
    log_directory = os.getenv("LOG_DIR", "logs")
    os.makedirs(log_directory, exist_ok=True)
    log_file = os.path.join(
        log_directory,
        f"llm_calls_{datetime.now().strftime('%Y%m%d')}.log"
    )

    logger = logging.getLogger("llm_logger")
    logger.setLevel(logging.INFO)
    logger.propagate = False  # Don't propagate to root logger

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(file_handler)
    return logger

logger = setup_logger()
cache_file = os.getenv("LLM_CACHE_FILE", "llm_cache.json")

# Wrapper for calling OpenAI o-series models with optional caching
def call_llm(prompt: str, use_cache: bool = True) -> str:
    """
    Send a prompt to the OpenAI thinking model (default: o4-mini) with chain-of-thought enabled.
    Caches responses in llm_cache.json by default.

    Args:
        prompt (str): The input prompt for the LLM.
        use_cache (bool): Whether to read/write from cache.

    Returns:
        str: The model's response text.
    """
    logger.info(f"PROMPT: {prompt}")

    # Load or check cache
    if use_cache and os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache = json.load(f)
            if prompt in cache:
                logger.info("CACHE HIT")
                logger.info(f"RESPONSE: {cache[prompt]}")
                return cache[prompt]
        except Exception:
            logger.warning("Failed to load cache; continuing without cache")

    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
    model_name = os.getenv("OPENAI_MODEL", "o4-mini")

    # Send chat completion request
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=4000,
        reasoning_effort="medium",
        store=False
    )
    response_text = response.choices[0].message.content

    logger.info(f"RESPONSE: {response_text}")

    # Write to cache
    if use_cache:
        try:
            cache = {}
            if os.path.exists(cache_file):
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
        except Exception:
            cache = {}

        cache[prompt] = response_text
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    return response_text

if __name__ == "__main__":
    test_prompt = "Hello, how are you?"
    print("Making call...")
    response = call_llm(test_prompt, use_cache=False)
    print(f"Response: {response}")
