# Progress Log

## 2025-05-07

### LLM Configuration Updates (Cline)

- **Objective**: Enhance `utils/call_llm.py` and `llm_config.json` to support various LLM providers via direct API endpoints and improve caching.

- **Key Changes & Verifications**:
    1.  **Gemini Provider Endpoint**:
        *   Updated `llm_config.json` to include an `api_endpoint` for the "gemini" provider.
        *   Modified `utils/call_llm.py` to use this direct endpoint for Gemini calls instead of relying solely on the `google-generativeai` SDK.
        *   Tested with model `gemini-2.5-flash-preview-04-17`. Confirmed working.
    2.  **OpenAI Provider Endpoint**:
        *   Updated `llm_config.json` to include an `api_endpoint` for the "openai" provider.
        *   Modified `utils/call_llm.py` to use this direct endpoint for OpenAI calls instead of the OpenAI SDK.
        *   Tested with model `o4-mini`. Confirmed working.
    3.  **Anthropic Provider Endpoint**:
        *   Updated `llm_config.json` to include an `api_endpoint` for the "anthropic" provider.
        *   Modified `utils/call_llm.py` to use this direct endpoint for Anthropic calls, including necessary headers (`x-api-key`, `anthropic-version`), instead of the Anthropic SDK.
        *   Tested with model `claude-3-7-sonnet-20250219`. Confirmed working.
    4.  **Multiple OpenRouter Models**:
        *   Refactored `llm_config.json` to support multiple, selectable OpenRouter configurations (e.g., `openrouter_gemini_flash`, `openrouter_llama_scout`).
        *   Updated `.env` with specific model environment variables for these configurations (`OPENROUTER_MODEL_GEMINI_FLASH`, `OPENROUTER_MODEL_LLAMA_SCOUT`).
        *   Modified `utils/call_llm.py` to correctly handle provider names starting with "openrouter_" to support these distinct configurations.
        *   Tested `meta-llama/Llama-4-Scout-17B-16E-Instruct` via `openrouter_llama_scout`. Confirmed working.
    5.  **Caching Mechanism with 10-Minute Expiry**:
        *   Updated `utils/call_llm.py` to store cache entries with timestamps.
        *   Cache lookup logic now checks if an entry is older than 10 minutes; if so, it's treated as expired.
        *   The `save_cache` function now prunes entries older than 10 minutes.
        *   Robustness added to handle transitions from old (string-based) cache formats to new (timestamped dictionary) formats.
        *   Confirmed working via test script.

- **Final State**:
    *   `utils/call_llm.py` now supports direct API calls for Gemini, OpenAI, and Anthropic if an `api_endpoint` is specified in their respective provider configurations in `llm_config.json`.
    *   OpenRouter configurations are now more granular, allowing selection of specific models.
    *   Caching includes a 10-minute expiry and pruning mechanism.
    *   The `active_provider` in `llm_config.json` has been reset to "gemini" after all tests.
