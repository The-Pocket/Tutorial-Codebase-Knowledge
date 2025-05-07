import os
import json
import logging
from datetime import datetime
import requests # Added for OpenRouter
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration Loading ---
# Construct the absolute path to llm_config.json relative to this script file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "llm_config.json"))
LLM_CONFIG = {}

def load_config():
    global LLM_CONFIG
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            LLM_CONFIG = json.load(f)
    else:
        # Fallback or error if config is essential
        print(f"Error: {CONFIG_FILE} not found. LLM calls may fail.")
        # Provide a minimal default config to prevent crashes if absolutely necessary
        LLM_CONFIG = {
            "active_provider": "gemini",
            "providers": {
                "gemini": {
                    "api_key_env": "GEMINI_API_KEY",
                    "model_env": "GEMINI_MODEL_PRIMARY",
                    "default_model": "gemini-2.5-flash-preview-04-17",
                    "client_type": "google_generativeai"
                }
            },
            "logging": {"default_log_directory": "logs", "log_prefix": "llm_calls_"},
            "caching": {"default_enabled": True, "cache_file_name": "llm_cache.json"}
        }

load_config()

# --- Logger Setup ---
logger = logging.getLogger("llm_logger")
logger.setLevel(logging.INFO)
logger.propagate = False

def setup_logger():
    log_config = LLM_CONFIG.get("logging", {})
    log_directory = os.getenv(log_config.get("log_directory_env"), log_config.get("default_log_directory", "logs"))
    os.makedirs(log_directory, exist_ok=True)
    log_prefix = log_config.get("log_prefix", "llm_calls_")
    log_file = os.path.join(log_directory, f"{log_prefix}{datetime.now().strftime('%Y%m%d')}.log")

    # Remove existing handlers to prevent duplicate logs if this function is called multiple times
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(file_handler)

setup_logger() # Initialize logger

# --- Cache Setup ---
CACHE_CONFIG = LLM_CONFIG.get("caching", {})
CACHE_ENABLED_ENV = CACHE_CONFIG.get("enabled_env")
DEFAULT_CACHE_ENABLED = CACHE_CONFIG.get("default_enabled", True)
CACHE_FILE_NAME = CACHE_CONFIG.get("cache_file_name", "llm_cache.json")

def is_cache_enabled():
    if CACHE_ENABLED_ENV:
        env_val = os.getenv(CACHE_ENABLED_ENV, "").lower()
        if env_val == "false":
            return False
        if env_val == "true":
            return True
    return DEFAULT_CACHE_ENABLED

def load_cache():
    if os.path.exists(CACHE_FILE_NAME):
        try:
            with open(CACHE_FILE_NAME, "r") as f:
                cache_data = json.load(f)
                # Basic validation for new structure (optional, but good practice)
                # For simplicity, we assume data is either old format (direct string) or new (dict with timestamp)
                return cache_data
        except json.JSONDecodeError:
            logger.warning(f"Failed to load cache from {CACHE_FILE_NAME}, starting with empty cache.")
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
    return {}

def save_cache(prompt_key, new_entry_data):
    """
    Saves a new entry to the cache and prunes expired entries.
    :param prompt_key: The prompt string (cache key).
    :param new_entry_data: A dict containing {"timestamp": ..., "response": ...}.
    """
    current_cache = load_cache()
    current_cache[prompt_key] = new_entry_data

    # Prune expired entries
    pruned_cache = {}
    current_timestamp = datetime.now().timestamp()
    CACHE_EXPIRY_SECONDS = 600  # 10 minutes

    for key, entry in current_cache.items():
        if isinstance(entry, dict) and "timestamp" in entry:
            entry_timestamp = entry.get("timestamp", 0)
            if (current_timestamp - entry_timestamp) < CACHE_EXPIRY_SECONDS:
                pruned_cache[key] = entry
            else:
                logger.info(f"Pruning expired cache entry for key: {key[:50]}...") # Log first 50 chars of key
        # else:
            # Optionally handle or log old format entries if any might exist during transition
            # For now, old format entries without timestamp would be effectively ignored by lookup
            # and eventually removed if not updated to new format.

    try:
        with open(CACHE_FILE_NAME, "w") as f:
            json.dump(pruned_cache, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save cache to {CACHE_FILE_NAME}: {e}")

# --- LLM Call Function ---
def call_llm(prompt: str) -> str:
    logger.info(f"PROMPT: {prompt}")
    use_cache_flag = is_cache_enabled()

    if use_cache_flag:
        cache = load_cache()
        cache_entry = cache.get(prompt)
        
        if isinstance(cache_entry, dict): # Check if it's new format
            entry_timestamp = cache_entry.get("timestamp", 0)
            entry_response = cache_entry.get("response")
            current_timestamp = datetime.now().timestamp()
            cache_age_seconds = current_timestamp - entry_timestamp
            
            CACHE_EXPIRY_SECONDS = 600  # 10 minutes
            if cache_age_seconds < CACHE_EXPIRY_SECONDS and entry_response is not None:
                logger.info(f"CACHE HIT - RESPONSE: {entry_response}")
                return entry_response
            else:
                logger.info(f"CACHE EXPIRED or malformed new-format entry for prompt: {prompt}")
        elif cache_entry is not None: # It's an old format string or other non-dict type
            logger.info(f"OLD CACHE FORMAT DETECTED and ignored for prompt: {prompt}")
        else: # cache_entry is None
            logger.info("CACHE MISS")

    active_provider_name = LLM_CONFIG.get("active_provider", "gemini") # Default to gemini if not set
    provider_config = LLM_CONFIG.get("providers", {}).get(active_provider_name)

    if not provider_config:
        error_msg = f"Configuration for active provider '{active_provider_name}' not found."
        logger.error(error_msg)
        raise ValueError(error_msg)

    api_key = os.getenv(provider_config["api_key_env"])
    model_name = os.getenv(provider_config["model_env"], provider_config["default_model"])

    if not api_key:
        error_msg = f"API key for {active_provider_name} (env var: {provider_config['api_key_env']}) not found."
        logger.error(error_msg)
        # Depending on strictness, could raise an error or return a default message
        return f"Error: API key for {active_provider_name} not configured."


    response_text = ""

    try:
        if active_provider_name == "gemini":
            api_endpoint_template = provider_config.get("api_endpoint")
            if not api_endpoint_template:
                error_msg = f"API endpoint for Gemini provider is not configured in llm_config.json."
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Replace {model} placeholder and append API key
            api_endpoint = api_endpoint_template.replace("{model}", model_name)
            full_api_endpoint = f"{api_endpoint}?key={api_key}"

            headers = {"Content-Type": "application/json"}
            # Gemini API expects a specific JSON structure for the request body
            data = {
                "contents": [{
                    "parts":[{
                        "text": prompt
                    }]
                }]
                # Add generationConfig if needed, e.g.,
                # "generationConfig": {
                #   "temperature": 0.9,
                #   "topK": 1,
                #   "topP": 1,
                #   "maxOutputTokens": 2048,
                #   "stopSequences": []
                # }
            }
            
            http_response = requests.post(full_api_endpoint, headers=headers, json=data)
            http_response.raise_for_status()
            response_json = http_response.json()
            
            # Extract text from the response, structure can vary
            # Based on typical Gemini API response:
            if response_json.get("candidates") and response_json["candidates"][0].get("content") and response_json["candidates"][0]["content"].get("parts"):
                response_text = "".join(part.get("text", "") for part in response_json["candidates"][0]["content"]["parts"])
            elif response_json.get("promptFeedback") and response_json["promptFeedback"].get("blockReason"):
                reason = response_json["promptFeedback"]["blockReason"]
                details = response_json["promptFeedback"].get("blockReasonMessage", "")
                error_msg = f"Gemini API call blocked. Reason: {reason}. Details: {details}"
                logger.error(error_msg)
                response_text = f"Error: {error_msg}"
            else:
                logger.warning(f"Unexpected Gemini API response structure: {response_json}")
                response_text = "Error: Could not parse Gemini API response."


        elif active_provider_name == "openai":
            api_endpoint = provider_config.get("api_endpoint")
            if not api_endpoint:
                error_msg = f"API endpoint for OpenAI provider is not configured in llm_config.json."
                logger.error(error_msg)
                raise ValueError(error_msg)

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}]
                # Add other OpenAI specific params like temperature, max_tokens if needed from provider_config
            }
            
            http_response = requests.post(api_endpoint, headers=headers, json=data)
            http_response.raise_for_status()
            response_json = http_response.json()
            response_text = response_json["choices"][0]["message"]["content"]

        elif active_provider_name == "anthropic":
            api_endpoint = provider_config.get("api_endpoint")
            if not api_endpoint:
                error_msg = f"API endpoint for Anthropic provider is not configured in llm_config.json."
                logger.error(error_msg)
                raise ValueError(error_msg)

            headers = {
                "x-api-key": api_key,
                "anthropic-version": provider_config.get("anthropic_version", "2023-06-01"), # Default or from config
                "Content-Type": "application/json"
            }
            data = {
                "model": model_name,
                "max_tokens": provider_config.get("max_tokens", 1024),
                "messages": [{"role": "user", "content": prompt}]
            }
            # Add thinking settings if enabled in config
            thinking_settings = provider_config.get("thinking_settings", {})
            if thinking_settings.get("enabled"):
                # Anthropic's direct API for "thinking" might be different or part of a beta
                # For now, we'll log a warning if "thinking" is enabled for direct API call
                # as it's typically a feature of their SDKs or specific client integrations.
                # If there's a direct API equivalent, this part would need adjustment.
                logger.warning("Anthropic 'thinking_settings' are configured, but direct API call for 'thinking' might require specific handling not yet implemented. Proceeding without 'thinking' block in direct API call.")
                # If the API supports a 'thinking' block directly, it would be added to 'data' here.
                # Example (hypothetical, check Anthropic docs for actual REST API structure for thinking):
                # data["thinking"] = {
                #     "type": "enabled", # Or however the API expects it
                #     "budget_tokens": thinking_settings.get("budget_tokens")
                # }


            http_response = requests.post(api_endpoint, headers=headers, json=data)
            http_response.raise_for_status()
            response_json = http_response.json()

            # Extract text from Anthropic's Messages API response
            if response_json.get("content") and isinstance(response_json["content"], list) and response_json["content"][0].get("type") == "text":
                response_text = "".join(block.get("text", "") for block in response_json["content"] if block.get("type") == "text")
            elif response_json.get("error"):
                err_type = response_json["error"].get("type")
                err_msg = response_json["error"].get("message")
                error_full_msg = f"Anthropic API Error: {err_type} - {err_msg}"
                logger.error(error_full_msg)
                response_text = f"Error: {error_full_msg}"
            else:
                logger.warning(f"Unexpected Anthropic API response structure: {response_json}")
                response_text = "Error: Could not parse Anthropic API response."

        elif active_provider_name.startswith("openrouter"): # Check if provider name starts with "openrouter"
            headers = {"Authorization": f"Bearer {api_key}"}
            data = {"model": model_name, "messages": [{"role": "user", "content": prompt}]}
            api_endpoint = provider_config.get("api_endpoint", "https://openrouter.ai/api/v1/chat/completions")
            
            http_response = requests.post(api_endpoint, headers=headers, json=data)
            http_response.raise_for_status() # Will raise an HTTPError for bad responses (4XX or 5XX)
            response_json = http_response.json()
            response_text = response_json["choices"][0]["message"]["content"]

        else:
            error_msg = f"LLM provider '{active_provider_name}' is not supported."
            logger.error(error_msg)
            raise NotImplementedError(error_msg)

    except requests.exceptions.RequestException as e:
        error_msg = f"API call to {active_provider_name} failed (network/http error): {e}"
        logger.error(error_msg)
        # Consider a more specific fallback or re-raise
        return f"Error: API call to {active_provider_name} failed. {e}"
    except Exception as e:
        error_msg = f"Error during LLM call with {active_provider_name} (model: {model_name}): {e}"
        logger.exception(error_msg) # Log full traceback
        # Consider a more specific fallback or re-raise
        return f"Error: LLM call failed. {e}"


    logger.info(f"RESPONSE: {response_text}")

    if use_cache_flag:
        new_cache_entry = {
            "timestamp": datetime.now().timestamp(),
            "response": response_text
        }
        # The save_cache function will now handle loading, updating with the new entry, pruning, and saving.
        save_cache(prompt, new_cache_entry)

    return response_text

# --- Main guard for testing ---
if __name__ == "__main__":
    # Ensure .env is loaded for testing if you rely on it here
    # from dotenv import load_dotenv
    # load_dotenv()

    # Reload config in case .env was just loaded for test
    load_config()
    setup_logger()


    print(f"LLM Configuration Loaded: {json.dumps(LLM_CONFIG, indent=2)}")
    print(f"Active provider: {LLM_CONFIG.get('active_provider')}")
    print(f"Cache enabled: {is_cache_enabled()}")
    
    # Create a dummy .env if it doesn't exist for the test to run
    # In a real scenario, the .env file should be properly set up.
    if not os.getenv(LLM_CONFIG["providers"][LLM_CONFIG["active_provider"]]["api_key_env"]):
        print(f"Warning: API key for {LLM_CONFIG['active_provider']} not found in environment. Test call might fail or use placeholders.")
        # Optionally, set a placeholder for some providers if they allow 'dry runs' or have test keys
        # For Gemini, an API key is generally required.

    test_prompt = "Hello, what is the capital of France? Respond in one word."
    
    print(f"\nMaking first call to '{LLM_CONFIG.get('active_provider')}' (model: {os.getenv(LLM_CONFIG['providers'][LLM_CONFIG['active_provider']]['model_env'], LLM_CONFIG['providers'][LLM_CONFIG['active_provider']]['default_model'])})...")
    response1 = call_llm(test_prompt)
    print(f"Response 1: {response1}")

    if is_cache_enabled():
        print("\nMaking second call (should hit cache if enabled)...")
        response2 = call_llm(test_prompt)
        print(f"Response 2: {response2}")

        if response1 == response2:
            print("\nCache test successful: Responses match.")
        else:
            print("\nCache test failed or first call failed: Responses do not match.")
    else:
        print("\nCaching is disabled, skipping cache test.")

    # Example of how to switch provider (for testing, normally done by changing llm_config.json)
    # And then call load_config() and setup_logger() again.
    # print("\n--- Testing with a different provider (if configured) ---")
    # original_provider = LLM_CONFIG['active_provider']
    # for provider_name in LLM_CONFIG['providers']:
    #     if provider_name != original_provider and os.getenv(LLM_CONFIG['providers'][provider_name]['api_key_env']):
    #         print(f"Switching to {provider_name} for a test call...")
    #         LLM_CONFIG['active_provider'] = provider_name # Temporarily switch for this test
    #         # Note: In a real app, you'd change llm_config.json and restart or reload config.
    #         # This direct modification is just for this isolated test script.
    #         # load_config() # Reread from file if changes were external
    #         # setup_logger() # Reinitialize logger if its config depends on provider

    #         current_provider_config = LLM_CONFIG['providers'][provider_name]
    #         model_to_use = os.getenv(current_provider_config['model_env'], current_provider_config['default_model'])
            
    #         print(f"Making call to '{provider_name}' (model: {model_to_use})...")
    #         try:
    #             response_other = call_llm(f"Hello from {provider_name}, what is 2+2?")
    #             print(f"Response from {provider_name}: {response_other}")
    #         except Exception as e:
    #             print(f"Could not test {provider_name}: {e}")
    #         LLM_CONFIG['active_provider'] = original_provider # Switch back
    #         break
    # else:
    #     print("No other providers with API keys found in .env for testing.")
