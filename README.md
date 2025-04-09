<h1 align="center">Turns Codebase into Easy Tutorial with AI</h1>

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

> *Ever stared at a new codebase written by others feeling completely lost? This tutorial shows you how to build an AI agent that analyzes GitHub repositories and creates beginner-friendly tutorials explaining exactly how the code works.*

<p align="center">
  <img 
    src="./assets/banner.png" width="800"
  />
</p>

This is a tutorial project of [Pocket Flow](https://github.com/The-Pocket/PocketFlow), a 100-line LLM framework. It crawls GitHub repositories and build a knowledge base from the code. It analyzes entire codebases to identify core abstractions and how they interact, and transforms complex code into beginner-friendly tutorials with clear visualizations.

- Check out the [YouTube Development Tutorial](https://youtu.be/AFY67zOpbSo) for more!

- Check out the [Substack Post Tutorial](https://zacharyhuang.substack.com/p/ai-codebase-knowledge-builder-full) for more!

## ⭐ Example Results for Popular GitHub Repositories!

<p align="center">
    <img 
      src="./assets/example.png" width="600"
    />
</p>

🤯 All these tutorials are generated **entirely by AI** by crawling the GitHub repo!

- [AutoGen Core](https://the-pocket.github.io/Tutorial-Codebase-Knowledge/AutoGen%20Core) - Build AI teams that talk, think, and solve problems together like coworkers!

- [Browser Use](https://the-pocket.github.io/Tutorial-Codebase-Knowledge/Browser%20Use) - Let AI surf the web for you, clicking buttons and filling forms like a digital assistant!

- [Celery](https://the-pocket.github.io/Tutorial-Codebase-Knowledge/Celery) - Supercharge your app with background tasks that run while you sleep!

- [Click](https://the-pocket.github.io/Tutorial-Codebase-Knowledge/Click) - Turn Python functions into slick command-line tools with just a decorator!

- [Crawl4AI](https://the-pocket.github.io/Tutorial-Codebase-Knowledge/Crawl4AI) - Train your AI to extract exactly what matters from any website!

- [CrewAI](https://the-pocket.github.io/Tutorial-Codebase-Knowledge/CrewAI) - Assemble a dream team of AI specialists to tackle impossible problems!

- [DSPy](https://the-pocket.github.io/Tutorial-Codebase-Knowledge/DSPy) - Build LLM apps like Lego blocks that optimize themselves!

- [FastAPI](https://the-pocket.github.io/Tutorial-Codebase-Knowledge/FastAPI) - Create APIs at lightning speed with automatic docs that clients will love!

- [Flask](https://the-pocket.github.io/Tutorial-Codebase-Knowledge/Flask) - Craft web apps with minimal code that scales from prototype to production!

- [LangGraph](https://the-pocket.github.io/Tutorial-Codebase-Knowledge/LangGraph) - Design AI agents as flowcharts where each step remembers what happened before!

- [LevelDB](https://the-pocket.github.io/Tutorial-Codebase-Knowledge/LevelDB) - Store data at warp speed with Google's engine that powers blockchains!

- [MCP Python SDK](https://the-pocket.github.io/Tutorial-Codebase-Knowledge/MCP%20Python%20SDK) - Build powerful apps that communicate through an elegant protocol without sweating the details!

- [NumPy Core](https://the-pocket.github.io/Tutorial-Codebase-Knowledge/NumPy%20Core) - Master the engine behind data science that makes Python as fast as C!

- [OpenManus](https://the-pocket.github.io/Tutorial-Codebase-Knowledge/OpenManus) - Build AI agents with digital brains that think, learn, and use tools just like humans do!

- [Pydantic Core](https://the-pocket.github.io/Tutorial-Codebase-Knowledge/Pydantic%20Core) - Validate data at rocket speed with just Python type hints!

- [Requests](https://the-pocket.github.io/Tutorial-Codebase-Knowledge/Requests) - Talk to the internet in Python with code so simple it feels like cheating!

- [SmolaAgents](https://the-pocket.github.io/Tutorial-Codebase-Knowledge/SmolaAgents) - Build tiny AI agents that punch way above their weight class!


## 🚀 Getting Started

### Option 1: Using Docker (Recommended)

1. Clone this repository

2. Configure your environment variables in the `.env` file:
   ```bash
   # Copy the sample .env file
   cp .env.sample .env
   
   # Edit the .env file with your credentials
   # GEMINI_PROJECT_ID=your-project-id
   # GITHUB_TOKEN=your-github-token
   ```

3. Run the application using Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. Access the Streamlit web interface at http://localhost:8501

### Option 2: Manual Installation

1. Clone this repository

2. Install dependencies: 
   ```bash
   pip install -r requirements.txt
   ```

3. Set up LLM in [`utils/call_llm.py`](./utils/call_llm.py) by providing credentials. By default, you can use the AI Studio key with this client for Gemini Pro 2.5:

   ```python
   client = genai.Client(
     api_key=os.getenv("GEMINI_API_KEY", "your-api_key"),
   )
   ```
  
   You can use your own models. We highly recommend the latest models with thinking capabilities (Claude 3.7 with thinking, O1). You can verify that it is correctly set up by running:
   ```bash
   python utils/call_llm.py
   ```
4. Run the Streamlit web interface:
   ```bash
   streamlit run app.py
   ```
   
   Or generate a complete codebase tutorial directly using the command line:
   ```bash
   python main.py https://github.com/username/repo --include "*.py" "*.js" --exclude "tests/*" --max-size 50000
   ```
   - `repo_url` - URL of the GitHub repository (required)
   - `-n, --name` - Project name (optional, derived from URL if omitted)
   - `-t, --token` - GitHub token (or set GITHUB_TOKEN environment variable)
   - `-o, --output` - Output directory (default: ./output)
   - `-i, --include` - Files to include (e.g., "*.py" "*.js")
   - `-e, --exclude` - Files to exclude (e.g., "tests/*" "docs/*")
   - `-s, --max-size` - Maximum file size in bytes (default: 100KB)
      
The application will crawl the repository, analyze the codebase structure, generate tutorial content, and save the output in the specified directory (default: ./output).


## 💡 Development Tutorial

- I built using [**Agentic Coding**](https://zacharyhuang.substack.com/p/agentic-coding-the-most-fun-way-to), the fastest development paradigm, where humans simply [design](docs/design.md) and agents [code](flow.py).

- The secret weapon is [Pocket Flow](https://github.com/The-Pocket/PocketFlow), a 100-line LLM framework that lets Agents (e.g., Cursor AI) build for you
  
- Check out the Step-by-step YouTube development tutorial: 

<br>
<div align="center">
  <a href="https://youtu.be/AFY67zOpbSo" target="_blank">
    <img src="./assets/youtube_thumbnail.png" width="500" alt="IMAGE ALT TEXT" style="cursor: pointer;">
  </a>
</div>
<br>
