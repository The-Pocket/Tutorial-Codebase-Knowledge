import dotenv
import os
import sys

# Adjust sys.path to allow imports from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flow import create_tutorial_flow

# Default file patterns (copied from main.py)
DEFAULT_INCLUDE_PATTERNS = {
    "*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.go", "*.java", "*.pyi", "*.pyx",
    "*.c", "*.cc", "*.cpp", "*.h", "*.md", "*.rst", "Dockerfile",
    "Makefile", "*.yaml", "*.yml",
}

DEFAULT_EXCLUDE_PATTERNS = {
    "assets/*", "data/*", "examples/*", "images/*", "public/*", "static/*", "temp/*",
    "docs/*", 
    "venv/*", ".venv/*", "*test*", "tests/*", "docs/*", "examples/*", "v1/*",
    "dist/*", "build/*", "experimental/*", "deprecated/*", "misc/*", 
    "legacy/*", ".git/*", ".github/*", ".next/*", ".vscode/*", "obj/*", "bin/*", "node_modules/*", "*.log"
}

dotenv.load_dotenv() # Load .env

def generate_tutorial_core(
    repo_url: str = None,
    local_dir: str = None,
    project_name: str = None,
    github_token: str = None,
    output_dir: str = "output",
    include_patterns: set = None,
    exclude_patterns: set = None,
    max_file_size: int = 100000,
    language: str = "english",
    use_cache: bool = True,
    max_abstractions: int = 10
):
    if include_patterns is None:
        include_patterns = DEFAULT_INCLUDE_PATTERNS
    if exclude_patterns is None:
        exclude_patterns = DEFAULT_EXCLUDE_PATTERNS

    actual_github_token = github_token
    if repo_url and not actual_github_token:
        actual_github_token = os.environ.get('GITHUB_TOKEN')
        if not actual_github_token:
            print("Warning: No GitHub token provided for repo_url. Rate limits might apply.")

    shared = {
        "repo_url": repo_url,
        "local_dir": local_dir,
        "project_name": project_name,
        "github_token": actual_github_token,
        "output_dir": output_dir,
        "include_patterns": include_patterns,
        "exclude_patterns": exclude_patterns,
        "max_file_size": max_file_size,
        "language": language,
        "use_cache": use_cache,
        "max_abstraction_num": max_abstractions,
        "files": [],
        "abstractions": [],
        "relationships": {},
        "chapter_order": [],
        "chapters": [],
        "final_output_dir": None
    }

    print(f"Starting tutorial generation for: {repo_url or local_dir} in {language.capitalize()} language")
    print(f"LLM caching: {'Enabled' if use_cache else 'Disabled'}")

    try:
        tutorial_flow = create_tutorial_flow()
        tutorial_flow.run(shared)
        final_output_dir = shared.get('final_output_dir')
        if final_output_dir:
            print(f"Tutorial generation complete. Output in: {final_output_dir}")
        else:
            print("Tutorial generation completed, but no output directory was reported by the flow.")
        return final_output_dir
    except Exception as e:
        print(f"Error during tutorial generation: {e}")
        # Potentially re-raise the exception or return a more specific error indicator
        raise e
