import os

# Test directory detection logic
output_base_dir = "output"
project_name = "GIM-BACK"

# Test with non-existent directory
non_existent_dir = "output/NON-EXISTENT"
print(f"\nTesting with non-existent directory: {non_existent_dir}")
if os.path.exists(non_existent_dir) and os.path.isdir(non_existent_dir):
    print(f"Directory exists: {non_existent_dir}")
else:
    print(f"Directory does not exist: {non_existent_dir}")
    
    # Try to find it in the output base directory
    if os.path.exists(output_base_dir) and os.path.isdir(output_base_dir):
        project_dirs = [d for d in os.listdir(output_base_dir) 
                       if os.path.isdir(os.path.join(output_base_dir, d))]
        
        print(f"Available project directories: {project_dirs}")
    else:
        print(f"Output base directory does not exist: {output_base_dir}")

print("\nTesting with existing directory:")

print(f"Checking if output directory exists: {output_base_dir}")
if os.path.exists(output_base_dir) and os.path.isdir(output_base_dir):
    print(f"Output base directory exists: {output_base_dir}")
    
    # List all directories in the output base directory
    project_dirs = [d for d in os.listdir(output_base_dir) 
                   if os.path.isdir(os.path.join(output_base_dir, d))]
    
    print(f"Found project directories: {project_dirs}")
    
    if project_name and project_name in project_dirs:
        # Found the project directory
        actual_output_dir = os.path.join(output_base_dir, project_name)
        print(f"Found project directory: {actual_output_dir}")
        
        # List files in the project directory
        files = os.listdir(actual_output_dir)
        print(f"Files in project directory: {files}")
    else:
        print(f"Project directory '{project_name}' not found in {output_base_dir}")
else:
    print(f"Output base directory does not exist: {output_base_dir}")