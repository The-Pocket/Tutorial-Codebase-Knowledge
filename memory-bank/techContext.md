# Technical Context

## LLM Integration (`utils/call_llm.py`)

- **Core Script**: `utils/call_llm.py` is the central script for interacting with various Large Language Models.
- **Configuration**:
    - LLM provider settings, API keys (via environment variable names), model names (via environment variable names or defaults), and API endpoints are managed in `llm_config.json`.
    - Environment variables (e.g., API keys, specific model overrides) are loaded from `.env`.
- **Supported Providers & Call Methods**:
    - **Gemini**: Supports direct API calls to the endpoint specified in `llm_config.json` (e.g., `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`).
    - **OpenAI**: Supports direct API calls to the endpoint specified in `llm_config.json` (e.g., `https://api.openai.com/v1/chat/completions`).
    - **Anthropic**: Supports direct API calls to the endpoint specified in `llm_config.json` (e.g., `https://api.anthropic.com/v1/messages`), including `x-api-key` and `anthropic-version` headers.
    - **OpenRouter**:
        - Supports direct API calls to the endpoint specified in `llm_config.json` (e.g., `https://openrouter.ai/api/v1/chat/completions`).
        - Multiple OpenRouter configurations can be defined in `llm_config.json` by naming providers with a common prefix (e.g., `openrouter_gemini_flash`, `openrouter_llama_scout`). The script handles these by checking if the active provider name starts with "openrouter".
        - Each specific OpenRouter configuration can have its own `model_env` and `default_model`.
- **Model Selection**:
    - The active LLM provider is determined by the `active_provider` field in `llm_config.json`.
    - For the active provider, the script first checks for a model name in the environment variable specified by `model_env` in its configuration.
    - If the environment variable is not set, it falls back to the `default_model` specified in the provider's configuration in `llm_config.json`.
- **Caching**:
    - Implemented in `utils/call_llm.py`.
    - Cache entries are stored in `llm_cache.json` (configurable).
    - Entries include a timestamp and the response: `{"prompt": {"timestamp": ..., "response": ...}}`.
    - Cache Expiry: 10 minutes (600 seconds). Expired entries are treated as misses.
    - Pruning: Expired entries are removed from `llm_cache.json` during save operations.
    - Handles transition from older, string-only cache formats.
- **Logging**:
    - LLM calls (prompts and responses) and cache activities are logged.
    - Log directory and prefix are configurable in `llm_config.json`.

## Key Files

- `llm_config.json`: Central configuration for LLM providers, models, endpoints, logging, and caching.
- `.env`: Stores sensitive API keys and allows overriding default model selections per provider.
- `utils/call_llm.py`: Script for making LLM calls, incorporating configuration, caching, and logging.
- `llm_cache.json`: Stores cached LLM responses.
