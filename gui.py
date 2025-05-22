import tkinter as tk
from tkinter import scrolledtext
import sys
import os
import threading
from flow import create_tutorial_flow # Assuming flow.py is in the same directory or PYTHONPATH

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

class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.text_widget.config(state=tk.NORMAL) # Ensure it's writable at init

    def write(self, string_val):
        # Ensure updates are done in the main thread if necessary
        # For ScrolledText, direct append from threads seems to work,
        # but using `after` is safer for general Tkinter widgets.
        self.text_widget.insert(tk.END, string_val)
        self.text_widget.see(tk.END) # Scroll to the end

    def flush(self):
        # Required for file-like object
        pass

class Application(tk.Frame):
    def __init__(self, master=None):
        if master is None:
            master = tk.Tk()
        super().__init__(master)
        self.master = master
        self.master.title("Codebase Tutorial Generator")
        self.pack(padx=10, pady=10)
        self.create_widgets()

        # Redirect stdout and stderr after output_area is created
        # Ensure output_area is writable before redirecting
        # Check if output_area exists, as it might not if create_widgets hasn't been called
        # or if this __init__ is part of a subclass that hasn't created it yet.
        # For this specific app, create_widgets is called right after pack.
        if hasattr(self, 'output_area'):
            self.output_area.config(state=tk.NORMAL)
            redirector = StdoutRedirector(self.output_area)
            sys.stdout = redirector
            sys.stderr = redirector
            self.output_area.config(state=tk.DISABLED) # Set back to disabled for user interaction
        else:
            # Fallback if output_area is not yet created, though for this app it should be.
            print("Warning: output_area not found for stdout/stderr redirection during __init__.")


    def create_widgets(self):
        # Input Fields and Labels
        row_index = 0

        # Repository URL
        tk.Label(self, text="Repository URL:").grid(row=row_index, column=0, sticky=tk.W, pady=2)
        self.repo_url_entry = tk.Entry(self, width=50)
        self.repo_url_entry.grid(row=row_index, column=1, pady=2)
        row_index += 1

        # Local Directory Path
        tk.Label(self, text="Local Directory Path:").grid(row=row_index, column=0, sticky=tk.W, pady=2)
        self.local_dir_entry = tk.Entry(self, width=50)
        self.local_dir_entry.grid(row=row_index, column=1, pady=2)
        row_index += 1

        # Radio buttons for Repo URL or Local Directory
        self.path_source_choice = tk.StringVar(value="repo_url")
        tk.Radiobutton(self, text="Use Repository URL", variable=self.path_source_choice, value="repo_url", command=self.toggle_path_inputs).grid(row=row_index, column=0, sticky=tk.W, columnspan=2)
        row_index += 1
        tk.Radiobutton(self, text="Use Local Directory Path", variable=self.path_source_choice, value="local_dir", command=self.toggle_path_inputs).grid(row=row_index, column=0, sticky=tk.W, columnspan=2)
        row_index += 1
        tk.Label(self, text="(Select one source for the codebase)").grid(row=row_index, column=0, columnspan=2, sticky=tk.W, pady=(0,5))
        row_index += 1

        # Project Name
        tk.Label(self, text="Project Name (optional):").grid(row=row_index, column=0, sticky=tk.W, pady=2)
        self.project_name_entry = tk.Entry(self, width=50)
        self.project_name_entry.grid(row=row_index, column=1, pady=2)
        row_index += 1

        # GitHub Token
        tk.Label(self, text="GitHub Token (optional):").grid(row=row_index, column=0, sticky=tk.W, pady=2)
        self.github_token_entry = tk.Entry(self, width=50, show='*')
        self.github_token_entry.grid(row=row_index, column=1, pady=2)
        row_index += 1

        # Output Directory
        tk.Label(self, text="Output Directory:").grid(row=row_index, column=0, sticky=tk.W, pady=2)
        self.output_dir_entry = tk.Entry(self, width=50)
        self.output_dir_entry.insert(0, "./output")
        self.output_dir_entry.grid(row=row_index, column=1, pady=2)
        row_index += 1

        # Include Patterns
        tk.Label(self, text="Include Patterns (space-separated):").grid(row=row_index, column=0, sticky=tk.W, pady=2)
        self.include_patterns_entry = tk.Entry(self, width=50)
        self.include_patterns_entry.insert(0, " ".join(DEFAULT_INCLUDE_PATTERNS))
        self.include_patterns_entry.grid(row=row_index, column=1, pady=2)
        row_index += 1

        # Exclude Patterns
        tk.Label(self, text="Exclude Patterns (space-separated):").grid(row=row_index, column=0, sticky=tk.W, pady=2)
        self.exclude_patterns_entry = tk.Entry(self, width=50)
        self.exclude_patterns_entry.insert(0, " ".join(DEFAULT_EXCLUDE_PATTERNS))
        self.exclude_patterns_entry.grid(row=row_index, column=1, pady=2)
        row_index += 1

        # Max File Size
        tk.Label(self, text="Max File Size (bytes):").grid(row=row_index, column=0, sticky=tk.W, pady=2)
        self.max_file_size_entry = tk.Entry(self, width=50)
        self.max_file_size_entry.insert(0, "100000")
        self.max_file_size_entry.grid(row=row_index, column=1, pady=2)
        row_index += 1

        # Language
        tk.Label(self, text="Language:").grid(row=row_index, column=0, sticky=tk.W, pady=2)
        self.language_entry = tk.Entry(self, width=50)
        self.language_entry.insert(0, "english")
        self.language_entry.grid(row=row_index, column=1, pady=2)
        row_index += 1

        # Max Abstractions
        tk.Label(self, text="Max Abstractions:").grid(row=row_index, column=0, sticky=tk.W, pady=2)
        self.max_abstractions_entry = tk.Entry(self, width=50)
        self.max_abstractions_entry.insert(0, "10")
        self.max_abstractions_entry.grid(row=row_index, column=1, pady=2)
        row_index += 1

        # Disable Cache Checkbox
        self.disable_cache_var = tk.BooleanVar()
        self.disable_cache_check = tk.Checkbutton(self, text="Disable Cache", variable=self.disable_cache_var)
        self.disable_cache_check.grid(row=row_index, column=0, columnspan=2, sticky=tk.W, pady=5)
        row_index += 1

        # Generate Tutorial Button
        self.generate_button = tk.Button(self, text="Generate Tutorial", command=self.start_generation_thread)
        self.generate_button.grid(row=row_index, column=0, columnspan=2, pady=10)
        row_index += 1

        # Output Area
        tk.Label(self, text="Output Log:").grid(row=row_index, column=0, sticky=tk.W, pady=2)
        row_index += 1
        self.output_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=70, height=15, state=tk.DISABLED)
        self.output_area.grid(row=row_index, column=0, columnspan=2, pady=5)
        row_index += 1

        # Quit Button (optional, for standalone testing)
        self.quit_button = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
        self.quit_button.grid(row=row_index, column=0, columnspan=2, pady=5, sticky=tk.E)

        self.toggle_path_inputs() # Set initial state of path inputs

    def toggle_path_inputs(self):
        choice = self.path_source_choice.get()
        if choice == "repo_url":
            self.repo_url_entry.config(state=tk.NORMAL)
            self.local_dir_entry.config(state=tk.DISABLED)
            self.github_token_entry.config(state=tk.NORMAL) # Enable token for repo
        else: # local_dir
            self.repo_url_entry.config(state=tk.DISABLED)
            self.local_dir_entry.config(state=tk.NORMAL)
            self.github_token_entry.config(state=tk.DISABLED) # Disable token for local


    def log_message(self, message, is_error=False):
        # This method is now primarily for direct calls if needed,
        # as stdout/stderr redirection handles most logs.
        # It ensures the text area is enabled before writing and disabled after.
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, message + "\n")
        self.output_area.see(tk.END)
        self.output_area.config(state=tk.DISABLED)

    def start_generation_thread(self):
        self.generate_button.config(state=tk.DISABLED) # Disable button during generation
        self.log_message("Starting tutorial generation...") # Use log_message
        thread = threading.Thread(target=self.generate_tutorial_logic)
        thread.daemon = True # Allow main program to exit even if thread is running
        thread.start()

    def generate_tutorial_logic(self):
        try:
            # 1. Retrieve Inputs
            path_choice = self.path_source_choice.get()
            repo_url = self.repo_url_entry.get() if path_choice == "repo_url" else None
            local_dir = self.local_dir_entry.get() if path_choice == "local_dir" else None

            project_name = self.project_name_entry.get() or None
            github_token_val = self.github_token_entry.get() or os.environ.get('GITHUB_TOKEN')

            output_dir = self.output_dir_entry.get() or "./output"

            include_patterns_str = self.include_patterns_entry.get()
            exclude_patterns_str = self.exclude_patterns_entry.get()

            include_patterns = set(include_patterns_str.split()) if include_patterns_str else DEFAULT_INCLUDE_PATTERNS
            exclude_patterns = set(exclude_patterns_str.split()) if exclude_patterns_str else DEFAULT_EXCLUDE_PATTERNS

            max_file_size_str = self.max_file_size_entry.get()
            language = self.language_entry.get() or "english"
            max_abstractions_str = self.max_abstractions_entry.get()
            use_cache = not self.disable_cache_var.get()

            # 2. Basic Validation
            if not repo_url and not local_dir:
                print("Error: Either Repository URL or Local Directory Path must be provided.")
                self.generate_button.config(state=tk.NORMAL)
                return

            try:
                max_file_size = int(max_file_size_str) if max_file_size_str else 100000
            except ValueError:
                print("Error: Max File Size must be a valid integer.")
                self.generate_button.config(state=tk.NORMAL)
                return

            try:
                max_abstractions = int(max_abstractions_str) if max_abstractions_str else 10
            except ValueError:
                print("Error: Max Abstractions must be a valid integer.")
                self.generate_button.config(state=tk.NORMAL)
                return
            
            if path_choice == "repo_url" and not repo_url:
                print("Error: Repository URL must be provided if 'Use Repository URL' is selected.")
                self.generate_button.config(state=tk.NORMAL)
                return
            if path_choice == "local_dir" and not local_dir:
                print("Error: Local Directory Path must be provided if 'Use Local Directory Path' is selected.")
                self.generate_button.config(state=tk.NORMAL)
                return


            # 3. Construct `shared` Dictionary
            shared = {
                "repo_url": repo_url,
                "local_dir": local_dir,
                "project_name": project_name,
                "github_token": github_token_val,
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
            print(f"Include patterns: {include_patterns}")
            print(f"Exclude patterns: {exclude_patterns}")


            # 4. Import and Run Flow
            tutorial_flow = create_tutorial_flow()
            tutorial_flow.run(shared)
            print("\nTutorial generation completed successfully!")
            if shared.get("final_output_dir"):
                print(f"Tutorial saved to: {os.path.abspath(shared['final_output_dir'])}")

        except Exception as e:
            print(f"An error occurred during tutorial generation: {e}")
            import traceback
            traceback.print_exc() # This will print to stderr, which is redirected
        finally:
            # Re-enable the button in the main thread
            self.master.after(0, lambda: self.generate_button.config(state=tk.NORMAL))


if __name__ == '__main__':
    # root = tk.Tk() # Master is now handled by Application's __init__
    app = Application()
    app.mainloop()
