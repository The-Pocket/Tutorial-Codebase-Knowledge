from google import genai
import os
import logging
import json
import requests
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

# Simple cache configuration
cache_file = "llm_cache.json"

def call_llm(prompt, use_cache: bool = True) -> str:
    """
    Call an LLM provider based on environment variables.
    Environment variables:
    - LLM_PROVIDER: "OLLAMA" or "XAI"
    - <provider>_MODEL: Model name (e.g., OLLAMA_MODEL, XAI_MODEL)
    - <provider>_BASE_URL: Base URL without endpoint (e.g., OLLAMA_BASE_URL, XAI_BASE_URL)
    - <provider>_API_KEY: API key (e.g., OLLAMA_API_KEY, XAI_API_KEY; optional for providers that don't require it)
    The endpoint /v1/chat/completions will be appended to the base URL.
    """
    logger.info(f"PROMPT: {prompt}") # log the prompt

    # Read the provider from environment variable
    provider = os.environ.get("LLM_PROVIDER")
    if not provider:
        raise ValueError("LLM_PROVIDER environment variable is required")

    # Construct the names of the other environment variables
    model_var = f"{provider}_MODEL"
    base_url_var = f"{provider}_BASE_URL"
    api_key_var = f"{provider}_API_KEY"

    # Read the provider-specific variables
    model = os.environ.get(model_var)
    base_url = os.environ.get(base_url_var)
    api_key = os.environ.get(api_key_var, "")  # API key is optional, default to empty string

    # Validate required variables
    if not model:
        raise ValueError(f"{model_var} environment variable is required")
    if not base_url:
        raise ValueError(f"{base_url_var} environment variable is required")

    # Append the endpoint to the base URL
    url = f"{base_url}/v1/chat/completions"

    # Configure headers and payload based on provider
    headers = {
        "Content-Type": "application/json",
    }
    if api_key:  # Only add Authorization header if API key is provided
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response_json = response.json() # Log the response
        logger.info("RESPONSE:\n%s", json.dumps(response_json, indent=2))
        #logger.info(f"RESPONSE: {response.json()}")
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as e:
        error_message = f"HTTP error occurred: {e}"
        try:
            error_details = response.json().get("error", "No additional details")
            error_message += f" (Details: {error_details})"
        except:
            pass
        raise Exception(error_message)
    except requests.exceptions.ConnectionError:
        raise Exception(f"Failed to connect to {provider} API. Check your network connection.")
    except requests.exceptions.Timeout:
        raise Exception(f"Request to {provider} API timed out.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"An error occurred while making the request to {provider}: {e}")
    except ValueError:
        raise Exception(f"Failed to parse response as JSON from {provider}. The server might have returned an invalid response.")

# By default, we Google Gemini 2.5 pro, as it shows great performance for code understanding
#def call_llm(prompt: str, use_cache: bool = True) -> str:
#    # Log the prompt
#    logger.info(f"PROMPT: {prompt}")
#
#    # Check cache if enabled
#    if use_cache:
#        # Load cache from disk
#        cache = {}
#        if os.path.exists(cache_file):
#            try:
#                with open(cache_file, 'r') as f:
#                    cache = json.load(f)
#            except:
#                logger.warning(f"Failed to load cache, starting with empty cache")
#
#        # Return from cache if exists
#        if prompt in cache:
#            logger.info(f"RESPONSE: {cache[prompt]}")
#            return cache[prompt]
#
#    # Call the LLM if not in cache or cache disabled
#    client = genai.Client(
#        vertexai=True,
#        # TODO: change to your own project id and location
#        project=os.getenv("GEMINI_PROJECT_ID", "your-project-id"),
#        location=os.getenv("GEMINI_LOCATION", "us-central1")
#    )
#    # You can comment the previous line and use the AI Studio key instead:
#    # client = genai.Client(
#    #     api_key=os.getenv("GEMINI_API_KEY", "your-api_key"),
#    # )
#    model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro-exp-03-25")
#    response = client.models.generate_content(
#        model=model,
#        contents=[prompt]
#    )
#    response_text = response.text
#
#    # Log the response
#    logger.info(f"RESPONSE: {response_text}")
#
#    # Update cache if enabled
#    if use_cache:
#        # Load cache again to avoid overwrites
#        cache = {}
#        if os.path.exists(cache_file):
#            try:
#                with open(cache_file, 'r') as f:
#                    cache = json.load(f)
#            except:
#                pass
#
#        # Add to cache and save
#        cache[prompt] = response_text
#        try:
#            with open(cache_file, 'w') as f:
#                json.dump(cache, f)
#        except Exception as e:
#            logger.error(f"Failed to save cache: {e}")
#
#    return response_text

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

