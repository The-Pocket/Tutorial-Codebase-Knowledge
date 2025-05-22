import dotenv
import os
import argparse
# Import the function that creates the flow
from webapp.core_runner import generate_tutorial_core # MODIFIED

dotenv.load_dotenv()

# Default file patterns are now in core_runner.py

# --- Main Function ---
def main():
    parser = argparse.ArgumentParser(description="Generate a tutorial for a GitHub codebase or local directory.")

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
    # Add language parameter for multi-language support
    parser.add_argument("--language", default="english", help="Language for the generated tutorial (default: english)")
    # Add use_cache parameter to control LLM caching
    parser.add_argument("--no-cache", action="store_true", help="Disable LLM response caching (default: caching enabled)")
    # Add max_abstraction_num parameter to control the number of abstractions
    parser.add_argument("--max-abstractions", type=int, default=10, help="Maximum number of abstractions to identify (default: 10)")

    args = parser.parse_args()

    # Get GitHub token from argument or environment variable if using repo
    # This logic is now handled within generate_tutorial_core
    github_token_to_pass = args.token # The core function will check env if this is None

    # Call the core function
    final_output_directory = generate_tutorial_core(
        repo_url=args.repo,
        local_dir=args.dir,
        project_name=args.name,
        github_token=github_token_to_pass,
        output_dir=args.output,
        include_patterns=set(args.include) if args.include else None,
        exclude_patterns=set(args.exclude) if args.exclude else None,
        max_file_size=args.max_size,
        language=args.language,
        use_cache=not args.no_cache,
        max_abstractions=args.max_abstractions
    )

    if final_output_directory:
        print(f"CLI run successful. Tutorial generated in: {final_output_directory}")
    else:
        print("CLI run completed, but no output directory was reported.")

if __name__ == "__main__":
    main()
