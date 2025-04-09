import os
import subprocess
import tempfile
import logging

logger = logging.getLogger(__name__)

def markdown_to_pdf(markdown_content, output_path=None):
    """
    Convert markdown content to PDF using pandoc.
    
    Args:
        markdown_content (str): The markdown content to convert
        output_path (str, optional): The path to save the PDF. If None, a temporary file will be created.
        
    Returns:
        str: The path to the generated PDF file
    """
    try:
        # Create a temporary file for the markdown content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_md:
            temp_md.write(markdown_content)
            temp_md_path = temp_md.name
        
        # Create a temporary file for the PDF output if not provided
        if output_path is None:
            temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            temp_pdf.close()
            output_path = temp_pdf.name
        
        # Create a CSS file for styling
        css_content = """
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #333;
            margin-top: 24px;
            margin-bottom: 16px;
        }
        h1 {
            font-size: 2em;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }
        h2 {
            font-size: 1.5em;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }
        code {
            font-family: 'Courier New', Courier, monospace;
            background-color: #f6f8fa;
            padding: 0.2em 0.4em;
            border-radius: 3px;
        }
        pre {
            background-color: #f6f8fa;
            border-radius: 3px;
            padding: 16px;
            overflow: auto;
        }
        pre code {
            background-color: transparent;
            padding: 0;
        }
        blockquote {
            border-left: 4px solid #dfe2e5;
            padding: 0 1em;
            color: #6a737d;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 16px;
        }
        table, th, td {
            border: 1px solid #dfe2e5;
        }
        th, td {
            padding: 6px 13px;
        }
        th {
            background-color: #f6f8fa;
        }
        img {
            max-width: 100%;
        }
        hr {
            height: 0.25em;
            padding: 0;
            margin: 24px 0;
            background-color: #e1e4e8;
            border: 0;
        }
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False) as temp_css:
            temp_css.write(css_content)
            temp_css_path = temp_css.name
        
        # Convert markdown to PDF using pandoc
        cmd = [
            'pandoc',
            temp_md_path,
            '-o', output_path,
            '--pdf-engine=xelatex',
            '-V', 'geometry:margin=1in',
            '--highlight-style=tango',
            '--standalone',
            '--css', temp_css_path,
            '--toc',  # Table of contents
            '--toc-depth=3',
            '--number-sections',
            '-V', 'colorlinks=true',
            '-V', 'linkcolor=blue',
            '-V', 'urlcolor=blue',
            '-V', 'toccolor=blue',
            '-f', 'markdown+yaml_metadata_block+raw_html+fenced_divs+mermaid',
            '--embed-resources',
            '--standalone'
        ]
        
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up temporary files
        os.unlink(temp_md_path)
        os.unlink(temp_css_path)
        
        if result.returncode != 0:
            logger.error(f"Error converting markdown to PDF: {result.stderr}")
            # Try alternative method with weasyprint
            return _markdown_to_pdf_weasyprint(markdown_content, output_path)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error in markdown_to_pdf: {str(e)}")
        # Try alternative method with weasyprint
        return _markdown_to_pdf_weasyprint(markdown_content, output_path)

def _markdown_to_pdf_weasyprint(markdown_content, output_path):
    """
    Alternative method to convert markdown to PDF using WeasyPrint.
    """
    try:
        import markdown
        from weasyprint import HTML, CSS
        from pymdownx.superfences import SuperFencesExtension
        from pymdownx.highlight import HighlightExtension
        
        # Convert markdown to HTML
        html = markdown.markdown(
            markdown_content,
            extensions=[
                'extra',
                'toc',
                'tables',
                'fenced_code',
                'codehilite',
                HighlightExtension(css_class='highlight'),
                SuperFencesExtension(custom_fences=[
                    {'name': 'mermaid', 'class': 'mermaid', 'format': lambda x, y, z: f'<div class="mermaid">{x}</div>'}
                ])
            ]
        )
        
        # Add CSS for styling
        css_content = """
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 2cm;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #333;
            margin-top: 24px;
            margin-bottom: 16px;
        }
        h1 {
            font-size: 2em;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }
        h2 {
            font-size: 1.5em;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }
        code {
            font-family: monospace;
            background-color: #f6f8fa;
            padding: 0.2em 0.4em;
            border-radius: 3px;
        }
        pre {
            background-color: #f6f8fa;
            border-radius: 3px;
            padding: 16px;
            overflow: auto;
        }
        pre code {
            background-color: transparent;
            padding: 0;
        }
        blockquote {
            border-left: 4px solid #dfe2e5;
            padding: 0 1em;
            color: #6a737d;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 16px;
        }
        table, th, td {
            border: 1px solid #dfe2e5;
        }
        th, td {
            padding: 6px 13px;
        }
        th {
            background-color: #f6f8fa;
        }
        img {
            max-width: 100%;
        }
        hr {
            height: 0.25em;
            padding: 0;
            margin: 24px 0;
            background-color: #e1e4e8;
            border: 0;
        }
        .highlight .hll { background-color: #ffffcc }
        .highlight .c { color: #999988; font-style: italic } /* Comment */
        .highlight .err { color: #a61717; background-color: #e3d2d2 } /* Error */
        .highlight .k { color: #000000; font-weight: bold } /* Keyword */
        .highlight .o { color: #000000; font-weight: bold } /* Operator */
        .highlight .cm { color: #999988; font-style: italic } /* Comment.Multiline */
        .highlight .cp { color: #999999; font-weight: bold; font-style: italic } /* Comment.Preproc */
        .highlight .c1 { color: #999988; font-style: italic } /* Comment.Single */
        .highlight .cs { color: #999999; font-weight: bold; font-style: italic } /* Comment.Special */
        .highlight .gd { color: #000000; background-color: #ffdddd } /* Generic.Deleted */
        .highlight .ge { color: #000000; font-style: italic } /* Generic.Emph */
        .highlight .gr { color: #aa0000 } /* Generic.Error */
        .highlight .gh { color: #999999 } /* Generic.Heading */
        .highlight .gi { color: #000000; background-color: #ddffdd } /* Generic.Inserted */
        .highlight .go { color: #888888 } /* Generic.Output */
        .highlight .gp { color: #555555 } /* Generic.Prompt */
        .highlight .gs { font-weight: bold } /* Generic.Strong */
        .highlight .gu { color: #aaaaaa } /* Generic.Subheading */
        .highlight .gt { color: #aa0000 } /* Generic.Traceback */
        .highlight .kc { color: #000000; font-weight: bold } /* Keyword.Constant */
        .highlight .kd { color: #000000; font-weight: bold } /* Keyword.Declaration */
        .highlight .kn { color: #000000; font-weight: bold } /* Keyword.Namespace */
        .highlight .kp { color: #000000; font-weight: bold } /* Keyword.Pseudo */
        .highlight .kr { color: #000000; font-weight: bold } /* Keyword.Reserved */
        .highlight .kt { color: #445588; font-weight: bold } /* Keyword.Type */
        .highlight .m { color: #009999 } /* Literal.Number */
        .highlight .s { color: #d01040 } /* Literal.String */
        .highlight .na { color: #008080 } /* Name.Attribute */
        .highlight .nb { color: #0086B3 } /* Name.Builtin */
        .highlight .nc { color: #445588; font-weight: bold } /* Name.Class */
        .highlight .no { color: #008080 } /* Name.Constant */
        .highlight .nd { color: #3c5d5d; font-weight: bold } /* Name.Decorator */
        .highlight .ni { color: #800080 } /* Name.Entity */
        .highlight .ne { color: #990000; font-weight: bold } /* Name.Exception */
        .highlight .nf { color: #990000; font-weight: bold } /* Name.Function */
        .highlight .nl { color: #990000; font-weight: bold } /* Name.Label */
        .highlight .nn { color: #555555 } /* Name.Namespace */
        .highlight .nt { color: #000080 } /* Name.Tag */
        .highlight .nv { color: #008080 } /* Name.Variable */
        .highlight .ow { color: #000000; font-weight: bold } /* Operator.Word */
        .highlight .w { color: #bbbbbb } /* Text.Whitespace */
        .highlight .mf { color: #009999 } /* Literal.Number.Float */
        .highlight .mh { color: #009999 } /* Literal.Number.Hex */
        .highlight .mi { color: #009999 } /* Literal.Number.Integer */
        .highlight .mo { color: #009999 } /* Literal.Number.Oct */
        .highlight .sb { color: #d01040 } /* Literal.String.Backtick */
        .highlight .sc { color: #d01040 } /* Literal.String.Char */
        .highlight .sd { color: #d01040 } /* Literal.String.Doc */
        .highlight .s2 { color: #d01040 } /* Literal.String.Double */
        .highlight .se { color: #d01040 } /* Literal.String.Escape */
        .highlight .sh { color: #d01040 } /* Literal.String.Heredoc */
        .highlight .si { color: #d01040 } /* Literal.String.Interpol */
        .highlight .sx { color: #d01040 } /* Literal.String.Other */
        .highlight .sr { color: #009926 } /* Literal.String.Regex */
        .highlight .s1 { color: #d01040 } /* Literal.String.Single */
        .highlight .ss { color: #990073 } /* Literal.String.Symbol */
        .highlight .bp { color: #999999 } /* Name.Builtin.Pseudo */
        .highlight .vc { color: #008080 } /* Name.Variable.Class */
        .highlight .vg { color: #008080 } /* Name.Variable.Global */
        .highlight .vi { color: #008080 } /* Name.Variable.Instance */
        .highlight .il { color: #009999 } /* Literal.Number.Integer.Long */
        """
        
        # Create a complete HTML document
        complete_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Tutorial</title>
            <style>
                {css_content}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        # Convert HTML to PDF
        HTML(string=complete_html).write_pdf(output_path)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error in _markdown_to_pdf_weasyprint: {str(e)}")
        # Try another alternative method with pdfkit
        return _markdown_to_pdf_pdfkit(markdown_content, output_path)

def _markdown_to_pdf_pdfkit(markdown_content, output_path):
    """
    Another alternative method to convert markdown to PDF using pdfkit (wkhtmltopdf).
    """
    try:
        import markdown
        import pdfkit
        
        # Convert markdown to HTML
        html = markdown.markdown(
            markdown_content,
            extensions=['extra', 'toc', 'tables', 'fenced_code', 'codehilite']
        )
        
        # Add CSS for styling
        css_content = """
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 2cm;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #333;
        }
        code {
            font-family: monospace;
            background-color: #f6f8fa;
            padding: 0.2em 0.4em;
            border-radius: 3px;
        }
        pre {
            background-color: #f6f8fa;
            border-radius: 3px;
            padding: 16px;
            overflow: auto;
        }
        """
        
        # Create a complete HTML document
        complete_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Tutorial</title>
            <style>
                {css_content}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        # Convert HTML to PDF
        options = {
            'page-size': 'A4',
            'margin-top': '2cm',
            'margin-right': '2cm',
            'margin-bottom': '2cm',
            'margin-left': '2cm',
            'encoding': 'UTF-8',
            'no-outline': None,
            'enable-local-file-access': None
        }
        
        pdfkit.from_string(complete_html, output_path, options=options)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error in _markdown_to_pdf_pdfkit: {str(e)}")
        # If all methods fail, return None
        return None