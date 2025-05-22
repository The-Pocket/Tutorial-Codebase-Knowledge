import os
import uuid
import shutil
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
import sys

# Ensure the root directory is in sys.path to allow imports like 'from webapp.core_runner ...'
# This is important if you run uvicorn from the root directory.
# If uvicorn is run from within webapp/, then 'from .core_runner ...' would be used.
# For consistency with how core_runner was handled, let's assume uvicorn will be run from root.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from webapp.core_runner import generate_tutorial_core, DEFAULT_INCLUDE_PATTERNS, DEFAULT_EXCLUDE_PATTERNS
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI()

# Mount static files directory
# Ensure this path is correct relative to where uvicorn is run.
# If running `uvicorn webapp.main_web:app` from the project root, "webapp/static" is correct.
app.mount("/static", StaticFiles(directory="webapp/static"), name="static")

# Base directory for storing outputs from web requests
WEB_OUTPUTS_BASE_DIR = Path("web_outputs")
WEB_OUTPUTS_BASE_DIR.mkdir(exist_ok=True)

# Path to the LLM cache file, ensure core_runner.py uses this or a configurable path
LLM_CACHE_FILE = Path("../llm_cache.json") # Adjust if core_runner.py's cache path is different
LOGS_DIR = Path("../logs") # Adjust if core_runner.py's log path is different

class TutorialRequest(BaseModel):
    repo_url: str
    project_name: str = None
    language: str = "english"
    include_patterns: list[str] = None
    exclude_patterns: list[str] = None
    max_file_size: int = 100000
    max_abstractions: int = 10
    github_token: str = None # Optional, core_runner will try os.environ if not given
    use_cache: bool = True

def run_generation_task(task_id: str, output_dir: Path, request_params: TutorialRequest):
    try:
        print(f"Task {task_id}: Starting generation in {output_dir}")
        # Convert list to set for include/exclude patterns if they are provided
        include_pats = set(request_params.include_patterns) if request_params.include_patterns else None
        exclude_pats = set(request_params.exclude_patterns) if request_params.exclude_patterns else None

        final_output_dir = generate_tutorial_core(
            repo_url=request_params.repo_url,
            local_dir=None, # Not supporting local_dir for web UI initially
            project_name=request_params.project_name,
            github_token=request_params.github_token,
            output_dir=str(output_dir), # Pass the unique task-specific output directory
            include_patterns=include_pats,
            exclude_patterns=exclude_pats,
            max_file_size=request_params.max_file_size,
            language=request_params.language,
            use_cache=request_params.use_cache,
            max_abstractions=request_params.max_abstractions
        )
        if final_output_dir:
            # Create a success marker file
            (output_dir / "_SUCCESS.txt").touch()
            print(f"Task {task_id}: Successfully generated tutorial at {final_output_dir}")
        else:
            (output_dir / "_FAILED.txt").touch()
            print(f"Task {task_id}: Failed to generate tutorial (core logic returned None).")

    except Exception as e:
        # Create a failure marker file
        (output_dir / "_FAILED.txt").touch()
        with open(output_dir / "error.log", "w") as f:
            f.write(str(e))
        print(f"Task {task_id}: Exception during tutorial generation: {e}")

@app.post("/generate-tutorial/")
async def create_tutorial_endpoint(request: TutorialRequest, background_tasks: BackgroundTasks):
    if not request.repo_url:
        raise HTTPException(status_code=400, detail="repo_url is required")

    task_id = str(uuid.uuid4())
    task_output_dir = WEB_OUTPUTS_BASE_DIR / task_id
    task_output_dir.mkdir(parents=True, exist_ok=True)

    background_tasks.add_task(run_generation_task, task_id, task_output_dir, request)

    return {"message": "Tutorial generation started.", "task_id": task_id, "status_url": f"/status/{task_id}", "results_url": f"/results/{task_id}/download"}

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task_output_dir = WEB_OUTPUTS_BASE_DIR / task_id
    if not task_output_dir.exists():
        raise HTTPException(status_code=404, detail="Task not found.")

    if (task_output_dir / "_SUCCESS.txt").exists():
        return {"task_id": task_id, "status": "completed", "output_directory": str(task_output_dir)}
    elif (task_output_dir / "_FAILED.txt").exists():
        error_log_path = task_output_dir / "error.log"
        error_message = "Error log not found."
        if error_log_path.exists():
            with open(error_log_path, "r") as f:
                error_message = f.read()
        return {"task_id": task_id, "status": "failed", "error_details": error_message}
    else:
        return {"task_id": task_id, "status": "processing"}

@app.get("/results/{task_id}/download")
async def download_tutorial_results(task_id: str):
    task_output_dir = WEB_OUTPUTS_BASE_DIR / task_id
    if not task_output_dir.exists() or not (task_output_dir / "_SUCCESS.txt").exists():
        raise HTTPException(status_code=404, detail="Tutorial not found or not yet complete.")

    # The `generate_tutorial_core` function saves its output into a subdirectory within `task_output_dir`.
    # This subdirectory is `final_output_dir` returned by `generate_tutorial_core`.
    # We need to find this directory to zip it.
    # Let's assume the success marker means there's one primary output folder inside.
    
    potential_output_dirs = [d for d in task_output_dir.iterdir() if d.is_dir()]
    
    actual_content_dir = task_output_dir # Default to task_output_dir
    
    # Attempt to find the actual content directory.
    # generate_tutorial_core creates output like: output_dir/project_name_language/
    # So, if task_output_dir is 'web_outputs/task_id/', then actual content is in
    # 'web_outputs/task_id/project_name_language/'.
    # We need to zip the contents of 'project_name_language'.
    
    if potential_output_dirs:
        # Heuristic: if there is only one subdirectory, assume it's the one.
        if len(potential_output_dirs) == 1:
            actual_content_dir = potential_output_dirs[0]
        else:
            # If multiple, it's ambiguous. For now, we'll log a warning and zip task_output_dir.
            # A more robust way would be to have generate_tutorial_core write the name of its
            # output subfolder to a known file, or for run_generation_task to capture it.
            print(f"Warning: Multiple subdirectories found in {task_output_dir}. Zipping the parent task directory.")
            # Or, we could try to find a directory that looks like a project name.
            # This part is tricky if project_name wasn't supplied to the request.
            # For now, zipping task_output_dir (which contains the actual output dir) is safer.
            # The user will get a zip containing "task_id/actual_project_output_dir/..."
            # This is acceptable for now.
            pass # actual_content_dir remains task_output_dir
            
    zip_filename_base = task_id
    zip_path = WEB_OUTPUTS_BASE_DIR / f"{zip_filename_base}_tutorial.zip"
    
    # We want to zip the *contents* of actual_content_dir, not actual_content_dir itself.
    # So, root_dir will be actual_content_dir, and base_dir will be '.' effectively.
    # However, shutil.make_archive's `root_dir` is the directory *containing* what you want to archive.
    # `base_dir` is the directory *itself* that you want to archive, relative to `root_dir`.
    # If we want a zip containing files from `actual_content_dir` directly at the top level of the zip:
    # Option 1: make_archive(str(zip_path.with_suffix('')), 'zip', root_dir=actual_content_dir, base_dir='.')
    # Option 2: make_archive(str(zip_path.with_suffix('')), 'zip', root_dir=actual_content_dir.parent, base_dir=actual_content_dir.name)
    # Let's use Option 1 to get the contents directly.

    try:
        shutil.make_archive(
            base_name=str(zip_path.with_suffix('')), # e.g. web_outputs/task_id_tutorial (no .zip)
            format='zip',
            root_dir=actual_content_dir, # The directory whose contents will be zipped
            base_dir='.' # Archive all files and subfolders from root_dir
        )
    except Exception as e:
        print(f"Error zipping directory {actual_content_dir}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create zip file: {e}")

    if zip_path.exists():
        return FileResponse(path=zip_path, filename=zip_path.name, media_type="application/zip")
    else:
        # This case should ideally be caught by the exception above.
        raise HTTPException(status_code=500, detail="Failed to create or find zip file after generation.")

# Placeholder for running with uvicorn if needed for quick testing
# if __name__ == "__main__":
#    import uvicorn
#    uvicorn.run(app, host="0.0.0.0", port=8000)
#    # To run from root: uvicorn webapp.main_web:app --reload

@app.get("/", response_class=HTMLResponse)
async def read_root():
    # Serve index.html from static directory
    # Ensure webapp/static/index.html exists
    try:
        with open("webapp/static/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="index.html not found. Ensure it is in webapp/static/index.html")
