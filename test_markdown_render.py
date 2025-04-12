import os

# Test directory
output_dir = "output/GIM-BACK"

# If the directory doesn't exist, try to find it
if not os.path.exists(output_dir):
    output_base_dir = "output"
    if os.path.exists(output_base_dir) and os.path.isdir(output_base_dir):
        project_dirs = [d for d in os.listdir(output_base_dir) 
                       if os.path.isdir(os.path.join(output_base_dir, d))]
        print(f"Available project directories: {project_dirs}")
        if project_dirs:
            output_dir = os.path.join(output_base_dir, project_dirs[0])
            print(f"Using first available directory: {output_dir}")

# Check if output directory exists
if os.path.exists(output_dir) and os.path.isdir(output_dir):
    print(f"Output directory exists: {output_dir}")
    
    # List files in the directory
    files = sorted(os.listdir(output_dir))
    print(f"Files in directory: {files}")
    
    # Read and print the content of each file
    for file in files:
        file_path = os.path.join(output_dir, file)
        if os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                print(f"\n--- {file} ---")
                print(f"First 100 characters: {content[:100]}...")
            except Exception as e:
                print(f"Error reading file {file}: {str(e)}")
else:
    print(f"Output directory does not exist: {output_dir}")