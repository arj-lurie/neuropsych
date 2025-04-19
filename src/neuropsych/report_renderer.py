# html_renderer.py

import os
import webbrowser

def render_summary_html(section_data: dict, fpath: str, output_filename="ai_generated_report.html"):
     # Get the directory from the input file path
    output_dir = os.path.dirname(fpath)
    # Combine directory and output filename
    output_file = os.path.join(output_dir, output_filename)

    html_sections = ""
    for section, result in section_data.items():
        html_sections += f"""
        <section class="content-section">
            <h2>Section: {section}</h2>
            <pre>{result}</pre>
        </section>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Generated Report</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f7f9fc;
                color: #333;
            }}
            .container {{
                max-width: 960px;
                margin: auto;
                padding: 20px;
            }}
            h1 {{
                text-align: center;
                color: #2c3e50;
                margin-bottom: 40px;
            }}
            .content-section {{
                background: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
                margin-bottom: 30px;
            }}
            h2 {{
                color: #1a73e8;
                font-size: 1.5em;
                margin-bottom: 10px;
            }}
            pre {{
                white-space: pre-wrap;
                background-color: #f4f4f4;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }}
            @media (max-width: 600px) {{
                body {{
                    padding: 10px;
                }}
                h1 {{
                    font-size: 1.8em;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>AI Summarization Results</h1>
            {html_sections}
        </div>
    </body>
    </html>
    """

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    webbrowser.open(f"file://{os.path.abspath(output_file)}")
