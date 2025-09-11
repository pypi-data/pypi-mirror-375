"""
Dashboard generator for Clever Logging.
Creates a standalone HTML dashboard that loads log data from a file.
"""

import os
from pathlib import Path
from datetime import datetime


def generate_dashboard(log_file_path: str, output_file: str = "logs_dashboard.html") -> str:
    """
    Generate a standalone HTML dashboard that loads log data from a file.
    
    Args:
        log_file_path: Path to the JSON log file
        output_file: Output HTML file name
        
    Returns:
        Path to the generated HTML file
    """
    
    # Get template file path
    template_path = Path(__file__).parent / "dashboard_template.html"
    
    # Read template
    with open(template_path, 'r', encoding='utf-8') as f:
        html_template = f.read()
    
    # Replace placeholders
    generation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html_content = html_template.replace("{{LOG_FILE_PATH}}", log_file_path)
    html_content = html_content.replace("{{GENERATION_DATE}}", generation_date)

    # Write the HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return os.path.abspath(output_file)


def generate_dashboard_from_file(json_file: str, output_file: str = "logs_dashboard.html") -> str:
    """
    Generate dashboard from a JSON log file.
    
    Args:
        json_file: Path to JSON log file
        output_file: Output HTML file name
        
    Returns:
        Path to the generated HTML file
    """
    
    # Check if input file exists
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"Log file not found: {json_file}")
    
    # Generate dashboard directly with the original file
    return generate_dashboard(json_file, output_file)

