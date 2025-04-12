import os
import tempfile
import subprocess
import logging
import base64
from pathlib import Path

logger = logging.getLogger(__name__)

def markdown_to_html(markdown_content):
    """
    Convert markdown content to HTML with proper rendering of code blocks and Mermaid diagrams.
    
    Args:
        markdown_content (str): The markdown content to convert
        
    Returns:
        str: The HTML content
    """
    try:
        # Create a temporary file for the markdown content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_md:
            temp_md.write(markdown_content)
            temp_md_path = temp_md.name
        
        # Create a temporary file for the HTML output
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp_html:
            temp_html_path = temp_html.name
        
        # Convert markdown to HTML using pandoc
        cmd = [
            'pandoc',
            temp_md_path,
            '-o', temp_html_path,
            '--standalone',
            '--highlight-style=tango',
            '--toc',
            '--toc-depth=3',
            '--number-sections',
            '-f', 'markdown+yaml_metadata_block+raw_html+fenced_divs+mermaid',
            '--embed-resources',
            '--mathjax',
            '--template=default',
            '--css', 'https://cdn.jsdelivr.net/npm/github-markdown-css/github-markdown.min.css',
            '--include-in-header', '-'
        ]
        
        # Add Mermaid script to the header
        mermaid_script = """
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                mermaid.initialize({
                    startOnLoad: true,
                    theme: 'default',
                    securityLevel: 'loose',
                    flowchart: { useMaxWidth: false, htmlLabels: true }
                });
            });
        </script>
        <style>
            .markdown-body {
                box-sizing: border-box;
                min-width: 200px;
                max-width: 980px;
                margin: 0 auto;
                padding: 45px;
            }
            @media (max-width: 767px) {
                .markdown-body {
                    padding: 15px;
                }
            }
            pre {
                background-color: #f6f8fa;
                border-radius: 3px;
                padding: 16px;
                overflow: auto;
            }
            code {
                font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
                background-color: rgba(27, 31, 35, 0.05);
                border-radius: 3px;
                padding: 0.2em 0.4em;
                margin: 0;
            }
            pre code {
                background-color: transparent;
                padding: 0;
            }
            .mermaid {
                text-align: center;
                margin: 20px 0;
            }
        </style>
        """
        
        # Run the command with the Mermaid script as input to --include-in-header
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        _, stderr = process.communicate(input=mermaid_script)
        
        if process.returncode != 0:
            logger.error(f"Error converting markdown to HTML: {stderr}")
            return None
        
        # Read the HTML content
        with open(temp_html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Clean up temporary files
        os.unlink(temp_md_path)
        os.unlink(temp_html_path)
        
        return html_content
    
    except Exception as e:
        logger.error(f"Error in markdown_to_html: {str(e)}")
        return None

def create_combined_markdown(files_dict, output_path=None):
    """
    Combine multiple markdown files into a single markdown file.
    
    Args:
        files_dict (dict): Dictionary mapping filenames to their content
        output_path (str, optional): Path to save the combined markdown file
        
    Returns:
        tuple: (combined_content, output_path)
    """
    try:
        # Start with index.md if it exists
        combined_content = ""
        if 'index.md' in files_dict:
            combined_content += files_dict['index.md'] + "\n\n---\n\n"
        
        # Add all numbered files in order
        numbered_files = sorted([f for f in files_dict.keys() 
                                if f.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')) 
                                and f.endswith('.md')])
        
        for file in numbered_files:
            combined_content += files_dict[file] + "\n\n---\n\n"
        
        # Add any remaining files
        for file in files_dict:
            if file != 'index.md' and file not in numbered_files and file.endswith('.md'):
                combined_content += files_dict[file] + "\n\n---\n\n"
        
        # Save to file if output_path is provided
        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(combined_content)
        
        return combined_content, output_path
    
    except Exception as e:
        logger.error(f"Error in create_combined_markdown: {str(e)}")
        return None, None

def html_to_pdf(html_content, output_path=None):
    """
    Convert HTML content to PDF using wkhtmltopdf.
    
    Args:
        html_content (str): The HTML content to convert
        output_path (str, optional): Path to save the PDF
        
    Returns:
        str: The path to the generated PDF
    """
    try:
        # Create a temporary file for the HTML content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp_html:
            temp_html.write(html_content)
            temp_html_path = temp_html.name
        
        # Create a temporary file for the PDF output if not provided
        if output_path is None:
            temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            temp_pdf.close()
            output_path = temp_pdf.name
        
        # Convert HTML to PDF using wkhtmltopdf
        cmd = [
            'wkhtmltopdf',
            '--enable-local-file-access',
            '--javascript-delay', '1000',  # Wait for JavaScript to execute (for Mermaid)
            '--no-stop-slow-scripts',
            '--margin-top', '20',
            '--margin-right', '20',
            '--margin-bottom', '20',
            '--margin-left', '20',
            '--page-size', 'A4',
            '--encoding', 'UTF-8',
            '--footer-center', '[page]/[topage]',
            temp_html_path,
            output_path
        ]
        
        # Run the command
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up temporary files
        os.unlink(temp_html_path)
        
        if process.returncode != 0:
            logger.error(f"Error converting HTML to PDF: {process.stderr}")
            return None
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error in html_to_pdf: {str(e)}")
        return None

def markdown_to_pdf(markdown_content, output_path=None):
    """
    Convert markdown content to PDF.
    
    Args:
        markdown_content (str): The markdown content to convert
        output_path (str, optional): Path to save the PDF
        
    Returns:
        str: The path to the generated PDF
    """
    # Convert markdown to HTML
    html_content = markdown_to_html(markdown_content)
    if not html_content:
        return None
    
    # Convert HTML to PDF
    return html_to_pdf(html_content, output_path)

def get_file_contents(directory, file_pattern=None):
    """
    Get the contents of all files in a directory.
    
    Args:
        directory (str): The directory to search
        file_pattern (str, optional): A pattern to match filenames
        
    Returns:
        dict: Dictionary mapping filenames to their content
    """
    try:
        files_dict = {}
        for file in os.listdir(directory):
            if file_pattern and not file.endswith(file_pattern):
                continue
            
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        files_dict[file] = f.read()
                except Exception as e:
                    logger.error(f"Error reading file {file}: {str(e)}")
        
        return files_dict
    
    except Exception as e:
        logger.error(f"Error in get_file_contents: {str(e)}")
        return {}