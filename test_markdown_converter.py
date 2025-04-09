import os
from utils.markdown_converter import markdown_to_html, markdown_to_pdf, create_combined_markdown, get_file_contents

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
    
    # Get file contents
    file_contents = get_file_contents(output_dir, '.md')
    print(f"Found {len(file_contents)} markdown files")
    
    # Create combined markdown
    combined_content, combined_file_path = create_combined_markdown(
        file_contents, 
        os.path.join(output_dir, "test_combined.md")
    )
    
    if combined_content and combined_file_path:
        print(f"Created combined markdown file: {combined_file_path}")
        
        # Convert to HTML
        html_content = markdown_to_html(combined_content)
        if html_content:
            html_file_path = os.path.join(output_dir, "test_combined.html")
            with open(html_file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Created HTML file: {html_file_path}")
        else:
            print("Failed to convert to HTML")
        
        # Convert to PDF
        pdf_file_path = os.path.join(output_dir, "test_combined.pdf")
        pdf_path = markdown_to_pdf(combined_content, pdf_file_path)
        if pdf_path and os.path.exists(pdf_path):
            print(f"Created PDF file: {pdf_path}")
        else:
            print("Failed to convert to PDF")
    else:
        print("Failed to create combined markdown")
else:
    print(f"Output directory does not exist: {output_dir}")