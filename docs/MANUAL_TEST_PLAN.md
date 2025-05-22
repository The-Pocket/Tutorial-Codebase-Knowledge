# Manual Test Plan for Code to Tutorial Web Application

## 1. Prerequisites & Setup

### 1.1. Environment Setup
- Ensure Python 3.8+ is installed.
- Clone the repository to your local machine.
- Create a virtual environment: `python -m venv .venv` and activate it: `source .venv/bin/activate` (or `.\.venv\Scripts\activate` on Windows).

### 1.2. Dependencies
- Install required Python packages: `pip install -r requirements.txt`.
- (If `pytest` was added for unit tests, ensure it's included in `requirements.txt` or install it separately: `pip install pytest`)

### 1.3. API Keys
- **Gemini API Key**: Obtain a Gemini API key from Google AI Studio.
- Set the API key as an environment variable:
  ```bash
  export GEMINI_API_KEY="YOUR_API_KEY_HERE"
  ```
  (On Windows, use `set GEMINI_API_KEY=YOUR_API_KEY_HERE` in Command Prompt or `$env:GEMINI_API_KEY="YOUR_API_KEY_HERE"` in PowerShell).
- **GitHub Token (Optional but Recommended)**: For accessing private repositories or avoiding rate limits on public ones, generate a GitHub Personal Access Token (PAT) with `repo` scope. This can be entered directly in the UI form or set as an environment variable `GITHUB_TOKEN`.

### 1.4. Running the Web Server
- Navigate to the project root directory in your terminal.
- Start the FastAPI application using Uvicorn:
  ```bash
  uvicorn webapp.main_web:app --reload
  ```
- The application should be accessible at `http://127.0.0.1:8000` in your web browser.

## 2. Test Cases

### 2.1. Test Case: Successful Tutorial Generation (Default Options)
- **Objective**: Verify successful tutorial generation for a valid public GitHub repository using default settings.
- **Steps**:
    1. Open the application in a web browser (`http://127.0.0.1:8000`).
    2. In the "GitHub Repository URL" field, enter a valid public GitHub repository URL (e.g., `https://github.com/pocket-flow/code-to-tutorial`).
    3. Leave all other fields as their default values (or blank for optional text fields).
    4. Ensure "Use LLM Cache" is checked.
    5. Click "Generate Tutorial".
- **Expected Results**:
    1. A "Processing..." message appears, followed by a "Request submitted. Task ID: ..." message.
    2. After some time, the status updates to "Tutorial Ready!".
    3. A download link "Download Tutorial (.zip)" appears.
    4. Clicking the link downloads a zip file.
    5. The zip file contains the generated tutorial files (markdown, images, etc.).
    6. Check `llm_cache.json` in the project root: it should be created and populated.
    7. Check `logs/llm_calls_YYYYMMDD.log`: it should contain logs of LLM interactions.

### 2.2. Test Case: Successful Tutorial Generation (Custom Options)
- **Objective**: Verify successful tutorial generation with custom parameters.
- **Steps**:
    1. Open the application.
    2. Enter a valid public GitHub repository URL (e.g., `https://github.com/tiangolo/fastapi`).
    3. Set "Project Name" to "FastAPI Test Tutorial".
    4. Change "Language" to "chinese" (if other languages are supported by LLM and prompts).
    5. Set "Include Patterns" to `*.py,README.md`.
    6. Set "Exclude Patterns" to `tests/*,docs/src/*`.
    7. Change "Max File Size" to `50000`.
    8. Change "Max Abstractions" to `5`.
    9. Optionally, enter a GitHub Token if testing with a private repo or to avoid rate limits.
    10. Click "Generate Tutorial".
- **Expected Results**:
    1. Similar to Test Case 2.1, a downloadable zip file is produced.
    2. The tutorial content should reflect the custom parameters (e.g., project name in titles, only specified files included, different language if applicable).
    3. Logs and cache should be updated.

### 2.3. Test Case: Invalid GitHub URL
- **Objective**: Verify how the system handles an invalid or non-existent GitHub URL.
- **Steps**:
    1. Open the application.
    2. Enter an invalid URL (e.g., `https://github.com/nonexistentuser/nonexistentrepo` or `htp://invalid-url.com`).
    3. Click "Generate Tutorial".
- **Expected Results**:
    1. The UI should display a "Processing..." message.
    2. After attempting to fetch the repo, the status area should update to "Tutorial Generation Failed."
    3. An error message should be displayed, indicating failure to fetch or process the repository (e.g., "Error: Error during tutorial generation: Failed to clone repository...").
    4. The `_FAILED.txt` and `error.log` files should be present in the corresponding `web_outputs/<task_id>/` directory.

### 2.4. Test Case: Missing GitHub URL (Client-Side & Server-Side Validation)
- **Objective**: Verify that the system requires the GitHub URL.
- **Steps (Client-side)**:
    1. Open the application.
    2. Leave the "GitHub Repository URL" field empty.
    3. Try to click "Generate Tutorial".
- **Expected Results (Client-side)**:
    1. The browser's HTML5 validation should prevent form submission, highlighting the required field.
- **Steps (Server-side - if client-side is bypassed)**:
    1. (Requires a tool like Postman or curl to bypass client-side validation) Send a POST request to `/generate-tutorial/` with an empty `repo_url`.
- **Expected Results (Server-side)**:
    1. The API should return a 400 Bad Request or 422 Unprocessable Entity error with a message indicating `repo_url` is required.

### 2.5. Test Case: Direct Status Endpoint Check
- **Objective**: Verify the `/status/{task_id}` endpoint directly.
- **Steps**:
    1. Initiate a valid tutorial generation (from Test Case 2.1). Note the `task_id` returned.
    2. While it's processing, open a new browser tab and navigate to `http://127.0.0.1:8000/status/{task_id}` (replace `{task_id}` with the actual ID).
    3. After completion, navigate to the same URL again.
    4. If a task failed (e.g., from Test Case 2.3), use its `task_id` with the status endpoint.
- **Expected Results**:
    1. While processing: JSON response with `{"task_id": "...", "status": "processing"}`.
    2. Upon success: JSON response with `{"task_id": "...", "status": "completed", "output_directory": "..."}`.
    3. Upon failure: JSON response with `{"task_id": "...", "status": "failed", "error_details": "..."}`.

### 2.6. Test Case: LLM Caching
- **Objective**: Verify that LLM caching works as expected.
- **Steps**:
    1. **First Run (Cache Misses)**:
        a. If `llm_cache.json` exists in the project root, delete it.
        b. Perform Test Case 2.1 (Successful Generation - Default Options) with a specific small public repository.
        c. Note the time taken and observe LLM call logs in `logs/`.
    2. **Second Run (Cache Hits)**:
        a. Without deleting `llm_cache.json`, perform the exact same request as in Step 1b (same repository, same default options).
        b. Note the time taken.
        c. Observe LLM call logs in `logs/`.
- **Expected Results**:
    1. `llm_cache.json` is created after the first run.
    2. The second run should complete significantly faster if the repository content hasn't changed and LLM calls are cacheable.
    3. Logs from the second run should indicate that responses are being served from the cache for identical prompts (the current `call_llm.py` logs this).

## 3. Cleanup
- Stop the Uvicorn server (Ctrl+C in the terminal).
- Deactivate the virtual environment: `deactivate`.
- **Optional**:
    - Delete the `web_outputs/` directory to remove generated tutorial task outputs.
    - Delete `llm_cache.json` to clear the LLM cache.
    - Delete the `logs/` directory to remove log files.

This manual test plan covers the main functionalities of the web application. Additional tests for specific edge cases or detailed feature variations can be added as needed.The manual test plan `docs/MANUAL_TEST_PLAN.md` was created in the previous turn.

Now, I will proceed with **Step 2: Write Unit Test for Pydantic Model**.

**2.a: Add `pytest` to `requirements.txt`**
First, I'll check if `pytest` is already in `requirements.txt`.
