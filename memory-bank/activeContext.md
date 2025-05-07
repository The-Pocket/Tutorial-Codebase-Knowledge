# Active Context: LLM Integration Enhancements

## Current Implementation Status

The `utils/call_llm.py` script has been significantly enhanced to provide a flexible and robust way to interact with multiple LLM providers.

**Key Features Implemented:**

1.  **Unified Configuration (`llm_config.json`, `.env`):**
    *   Centralized configuration for providers, API keys (via env vars), model names (via env vars or defaults), and API endpoints.
    *   Supports easy switching of the `active_provider`.

2.  **Direct API Endpoint Support:**
    *   **Gemini**: Can now be called via its direct REST API endpoint.
    *   **OpenAI**: Can now be called via its direct REST API endpoint.
    *   **Anthropic**: Can now be called via its direct REST API endpoint (Messages API), including required headers.
    *   **OpenRouter**: Continues to be supported via its direct API endpoint.

3.  **Flexible OpenRouter Model Selection:**
    *   `llm_config.json` allows defining multiple specific OpenRouter configurations (e.g., `openrouter_gemini_flash`, `openrouter_llama_scout`).
    *   The script correctly identifies and uses these specific configurations if set as `active_provider`.
    *   Model selection for these specific OpenRouter configurations is managed via dedicated environment variables (e.g., `OPENROUTER_MODEL_LLAMA_SCOUT`).

4.  **Advanced Caching Mechanism:**
    *   **Timestamped Entries**: Cache entries are stored with a timestamp.
    *   **10-Minute Expiry**: Cached responses older than 10 minutes are considered stale and will trigger a fresh API call.
    *   **Pruning**: Expired entries are automatically removed from the `llm_cache.json` file during save operations.
    *   **Format Resilience**: The cache loading logic can handle older, string-only cache entries, treating them as misses to facilitate a smooth transition to the new timestamped format.

5.  **Logging:**
    *   Comprehensive logging of prompts, responses, cache hits/misses, and errors.

## Current `llm_config.json` Structure for Providers:

```json
{
  "active_provider": "gemini", // Example, can be changed
  "providers": {
    "gemini": {
      "api_key_env": "GEMINI_API_KEY",
      "model_env": "GEMINI_MODEL_PRIMARY",
      "default_model": "gemini-2.5-flash-preview-04-17",
      "api_endpoint": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    },
    "openai": {
      "api_key_env": "OPENAI_API_KEY",
      "model_env": "OPENAI_MODEL_PRIMARY",
      "default_model": "gpt-4o-mini",
      "api_endpoint": "https://api.openai.com/v1/chat/completions"
    },
    "anthropic": {
      "api_key_env": "ANTHROPIC_API_KEY",
      "model_env": "ANTHROPIC_MODEL_PRIMARY",
      "default_model": "claude-3-5-haiku-20241022",
      "api_endpoint": "https://api.anthropic.com/v1/messages",
      "max_tokens": 21000,
      "thinking_settings": { // Note: 'thinking' via direct API might need specific handling
        "enabled": true,
        "budget_tokens": 20000
      }
    },
    "openrouter_gemini_flash": {
      "api_key_env": "OPENROUTER_API_KEY",
      "model_env": "OPENROUTER_MODEL_GEMINI_FLASH",
      "default_model": "google/gemini-2.5-flash-preview-04-17",
      "api_endpoint": "https://openrouter.ai/api/v1/chat/completions"
    },
    "openrouter_llama_scout": {
      "api_key_env": "OPENROUTER_API_KEY",
      "model_env": "OPENROUTER_MODEL_LLAMA_SCOUT",
      "default_model": "meta-llama/Llama-4-Scout-17B-16E-Instruct",
      "api_endpoint": "https://openrouter.ai/api/v1/chat/completions"
    }
  },
  // ... logging and caching configs ...
}
```

## Next Steps / Considerations:

*   **Error Handling & Fallbacks**: While basic error handling is in place, more sophisticated fallback strategies (e.g., trying a secondary model or provider on failure) could be considered if required.
*   **Streaming Support**: Currently, responses are handled synchronously. Adding support for streaming responses could be beneficial for user experience with slower models.
*   **Anthropic "Thinking" via Direct API**: The `thinking_settings` for Anthropic are noted in the script with a warning. If direct API support for "thinking" is available and different from SDK, this would need specific implementation in the `requests.post` call for Anthropic.
*   **Configuration for `generationConfig` (Gemini) / other model params**: The script currently sends a basic prompt. For more control over generation (temperature, max tokens, etc.), these parameters could be added to `llm_config.json` and passed in the `data` payload of the API calls.
*   **Testing with a wider range of models** for each configured provider to ensure compatibility.
