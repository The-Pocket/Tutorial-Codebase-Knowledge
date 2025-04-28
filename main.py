import dotenv
import os
import argparse
import sys
import textwrap
# Import the function that creates the flow
from flow import create_tutorial_flow
from utils.call_llm import call_llm

# Load environment variables from .env file if present
dotenv.load_dotenv()

# Default file patterns
DEFAULT_INCLUDE_PATTERNS = {
    "*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.go", "*.java", "*.pyi", "*.pyx",
    "*.c", "*.cc", "*.cpp", "*.h", "*.md", "*.rst", "Dockerfile",
    "Makefile", "*.yaml", "*.yml",
}

DEFAULT_EXCLUDE_PATTERNS = {
    "venv/*", ".venv/*", "*test*", "tests/*", "docs/*", "examples/*", "v1/*",
    "dist/*", "build/*", "experimental/*", "deprecated/*",
    "legacy/*", ".git/*", ".github/*", ".next/*", ".vscode/*", "obj/*", "bin/*", "node_modules/*", "*.log"
}

# Validate setup function
def validate_setup():
    # Test LLM configuration
    try:
        print("Validating LLM setup...")
        call_llm("Hello, testing LLM connection.", use_cache=False)
        print("✅ LLM connection successful!")
    except Exception as e:
        print(f"\n❌ LLM configuration error: {str(e)}")
        print("\nPlease check your LLM setup. See SETUP.md for detailed instructions.")
        return False
    return True

# --- Main Function ---
def main():
    parser = argparse.ArgumentParser(
        description="Generate a tutorial for a GitHub codebase or local directory.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''
            Example commands:
            -----------------
            # Generate tutorial from GitHub repo:
            python main.py --repo https://github.com/username/repo --include "*.py" "*.js" --exclude "tests/*"

            # Generate tutorial from local directory:
            python main.py --dir ./my-project --include "*.py" --max-size 200000

            # Generate tutorial in Chinese:
            python main.py --repo https://github.com/username/repo --language "Chinese"
            
            For detailed setup instructions, see SETUP.md
        ''')
    )

    # Create mutually exclusive group for source
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--repo", help="URL of the public GitHub repository.")
    source_group.add_argument("--dir", help="Path to local directory.")

    parser.add_argument("-n", "--name", help="Project name (optional, derived from repo/directory if omitted).")
    parser.add_argument("-t", "--token", help="GitHub personal access token (optional, reads from GITHUB_TOKEN env var if not provided).")
    parser.add_argument("-o", "--output", default="output", help="Base directory for output (default: ./output).")
    parser.add_argument("-i", "--include", nargs="+", help="Include file patterns (e.g. '*.py' '*.js'). Defaults to common code files if not specified.")
    parser.add_argument("-e", "--exclude", nargs="+", help="Exclude file patterns (e.g. 'tests/*' 'docs/*'). Defaults to test/build directories if not specified.")
    parser.add_argument("-s", "--max-size", type=int, default=100000, help="Maximum file size in bytes (default: 100000, about 100KB).")
    parser.add_argument("--language", default="english", help="Language for the generated tutorial (default: english)")
    parser.add_argument("--skip-validation", action="store_true", help="Skip validation of LLM setup")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Set verbose mode if requested
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.INFO)

    # Validate environment and setup unless skipped
    if not args.skip_validation:
        if not validate_setup():
            sys.exit(1)

    # Get GitHub token from argument or environment variable if using repo
    github_token = None
    if args.repo:
        github_token = args.token or os.environ.get('GITHUB_TOKEN')
        if not github_token:
            print("Warning: No GitHub token provided. You might hit rate limits for public repositories.")
            print("For better experience, set the GITHUB_TOKEN environment variable or use the --token option.")

    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)

    # Initialize the shared dictionary with inputs
    shared = {
        "repo_url": args.repo,
        "local_dir": args.dir,
        "project_name": args.name, # Can be None, FetchRepo will derive it
        "github_token": github_token,
        "output_dir": args.output, # Base directory for CombineTutorial output

        # Add include/exclude patterns and max file size
        "include_patterns": set(args.include) if args.include else DEFAULT_INCLUDE_PATTERNS,
        "exclude_patterns": set(args.exclude) if args.exclude else DEFAULT_EXCLUDE_PATTERNS,
        "max_file_size": args.max_size,

        # Add language for multi-language support
        "language": args.language,

        # Outputs will be populated by the nodes
        "files": [],
        "abstractions": [],
        "relationships": {},
        "chapter_order": [],
        "chapters": [],
        "final_output_dir": None
    }

    # Display starting message with repository/directory and language
    source_info = args.repo if args.repo else args.dir
    print(f"Starting tutorial generation for: {source_info}")
    print(f"Language: {args.language.capitalize()}")
    print(f"Output directory: {os.path.abspath(args.output)}")
    print(f"Maximum file size: {args.max_size} bytes")
    print(f"Include patterns: {shared['include_patterns']}")
    print(f"Exclude patterns: {shared['exclude_patterns']}")
    
    try:
        # Create the flow instance
        tutorial_flow = create_tutorial_flow()

        # Run the flow
        tutorial_flow.run(shared)
        
        # Show final success message with output location
        if shared.get("final_output_dir"):
            print(f"\n✅ Tutorial generation complete!")
            print(f"Output directory: {os.path.abspath(shared['final_output_dir'])}")
            print(f"Main tutorial index: {os.path.join(os.path.abspath(shared['final_output_dir']), 'index.md')}")
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error generating tutorial: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print("Run with --verbose for more details")
        sys.exit(1)

if __name__ == "__main__":
    main()
