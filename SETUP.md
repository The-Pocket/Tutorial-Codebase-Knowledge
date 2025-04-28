# Detailed Setup Guide for AI Codebase Knowledge Builder

This guide provides comprehensive instructions for setting up and configuring the AI Codebase Knowledge Builder tool.

## Prerequisites

- Python 3.8 or newer
- Git (for cloning repositories)
- Access to at least one of the supported LLM providers:
  - Google Gemini (default)
  - Anthropic Claude (optional)
  - OpenAI (optional)

## Step 1: Clone the Repository

```bash
git clone https://github.com/The-Pocket/Tutorial-Codebase-Knowledge.git
cd Tutorial-Codebase-Knowledge
```

## Step 2: Create and Activate a Virtual Environment (Recommended)

### For Linux/macOS
```bash
python -m venv venv
source venv/bin/activate
```

### For Windows
```bash
python -m venv venv
venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Configure LLM Access

You need to set up access to at least one Language Model provider. The project uses Google Gemini by default but supports others.

### Option 1: Google Gemini (Default)

Choose one of these methods:

#### Using Vertex AI
1. Create a Google Cloud project and enable Vertex AI
2. Set environment variables:
   ```bash
   export GEMINI_PROJECT_ID="your-project-id"
   export GEMINI_LOCATION="us-central1"  # Or your preferred region
   ```
   For Windows:
   ```
   set GEMINI_PROJECT_ID=your-project-id
   set GEMINI_LOCATION=us-central1
   ```

#### Using AI Studio
1. Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set the API key as an environment variable:
   ```bash
   export GEMINI_API_KEY="your-api-key"
   ```
   For Windows:
   ```
   set GEMINI_API_KEY=your-api-key
   ```

### Option 2: Anthropic Claude

1. Get an API key from [Anthropic](https://console.anthropic.com/)
2. Set the API key:
   ```bash
   export ANTHROPIC_API_KEY="your-api-key"
   ```
   For Windows:
   ```
   set ANTHROPIC_API_KEY=your-api-key
   ```
3. Edit `utils/call_llm.py` to uncomment the Claude implementation and comment out other implementations

### Option 3: OpenAI

1. Get an API key from [OpenAI](https://platform.openai.com/)
2. Set the API key:
   ```bash
   export OPENAI_API_KEY="your-api-key"
   ```
   For Windows:
   ```
   set OPENAI_API_KEY=your-api-key
   ```
3. Edit `utils/call_llm.py` to uncomment the OpenAI implementation and comment out other implementations

## Step 5: GitHub Token (Optional but Recommended)

For accessing GitHub repositories, especially private ones or to avoid rate limits:

1. Generate a GitHub token at [GitHub Settings](https://github.com/settings/tokens)
   - For public repositories: Select `public_repo` scope
   - For private repositories: Select `repo` scope
2. Set the token:
   ```bash
   export GITHUB_TOKEN="your-github-token"
   ```
   For Windows:
   ```
   set GITHUB_TOKEN=your-github-token
   ```

## Step 6: Verify Setup

Test your LLM configuration:

```bash
python utils/call_llm.py
```

You should see a response from the configured LLM provider.

## Troubleshooting

### LLM Connection Issues
- **Error**: "Failed to connect to LLM API"
  - Check your API keys and environment variables
  - Verify network connection
  - Ensure the correct model name is specified

### GitHub Access Issues
- **Error**: "Repository not found"
  - Check if the repository exists and is accessible
  - Verify GitHub token permissions
  - For private repositories, ensure your token has the `repo` scope

### File Size Limitations
- **Error**: "Skipping file: size exceeds limit"
  - Increase the `--max-size` parameter for larger files
  - Or exclude large files using the `--exclude` parameter

## Additional Configuration

- Create a `.env` file in the project root to store environment variables permanently
- Customize logging by modifying the `LOG_DIR` environment variable
- Adjust caching behavior by editing the cache settings in `utils/call_llm.py`

For more information, refer to the main [README.md](./README.md).
