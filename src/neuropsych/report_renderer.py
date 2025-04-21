# html_renderer.py
from jinja2 import Template
import os
import webbrowser

def render_summary_html(section_data: dict, fpath: str, patient_info: dict, output_filename="ai_generated_report.html"):
    # Get the directory from the input file path
    output_dir = os.path.dirname(fpath)
    # Combine directory and output filename
    output_file = os.path.join(output_dir, output_filename)

    # Generate navigation links
    nav_links = ""
    html_sections = ""
    for idx, (section, result) in enumerate(section_data.items()):
        section_id = f"section-{idx}"
        nav_links += f'<li><a href="#{section_id}" class="nav-link">{section}</a></li>'
        html_sections += f"""
        <section class="content-section" id="{section_id}">
            <h2>{section}</h2>
            <pre>{result}</pre>
        </section>
        """
    # Patient Info Table (Jinja2-style placeholders)
    patient_info_html = """
    <div class="patient-info">
        <table>
            <tr><td>PATIENT NAME:</td><td>{{ patient_info['name'] }}</td></tr>
            <tr><td>MEDICAL RECORD NO:</td><td>{{ patient_info['medical_record_no'] }}</td></tr>
            <tr><td>DATE OF BIRTH:</td><td>{{ patient_info['date_of_birth'] }}</td></tr>
            <tr><td>DATES OF SERVICE:</td><td>{{ patient_info['dates_of_service'] }}</td></tr>
            <tr><td>AGE AT EVALUATION:</td><td>{{ patient_info['age_at_evaluation'] }}</td></tr>
            <tr><td>EXAMINERS:</td><td>{{ patient_info['examiners'] | join('<br>') }}</td></tr>
        </table>
    </div>
    """
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Comprehensive Neuropsychological Evaluation</title>        
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Helvetica Neue", sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f7fa;
                color: #333;
            }}
            .container {{
                display: flex;
                max-width: 1100px;
                margin: auto;
            }}
            .nav-pane {{
                width: 240px;
                background: rgba(255, 255, 255, 0.9);  /* Translucent white */
                color: #333;
                padding: 10px;
                position: fixed;
                top: 0;
                left: 0;
                bottom: 0;
                overflow-y: auto;
                border-right: 1px solid rgba(0, 0, 0, 0.1);
                box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
                transition: width 0.3s;
            }}
            .nav-pane a {{
                color: #444;
                text-decoration: none;
                font-size: 1.1em;
                margin: 8px 0;
                display: block;
                padding: 6px 10px;
                border-radius: 4px;
                transition: background-color 0.3s;
            }}
            .nav-pane a:hover {{
                background-color: rgba(0, 122, 255, 0.1);
            }}
            .content {{
                margin-left: 260px;
                padding: 15px 25px;
                flex: 1;
            }}
            h1 {{
                text-align: center;
                color: #2c3e50;
                margin-bottom: 30px;
                font-size: 2em;
            }}
            .content-section {{
                background: rgba(255, 255, 255, 0.85); /* Translucent background */
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
                transition: max-height 0.3s ease-out;
            }}
            h2 {{
                color: #007aff;  /* Soft Apple-like blue */
                font-size: 1.6em;
                margin-bottom: 10px;
                cursor: pointer;
                padding: 5px 0;
                font-weight: 500;
            }}
            pre {{
                white-space: pre-wrap;
                background-color: #f6f8fa;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
                margin-top: 10px;
                font-size: 1em;
            }}
            /* Add subtle hover effects for sections */
            .content-section:hover {{
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }}
            @media (max-width: 768px) {{
                .container {{
                    flex-direction: column;
                }}
                .nav-pane {{
                    width: 100%;
                    position: relative;
                    top: auto;
                    left: auto;
                    bottom: auto;
                    box-shadow: none;
                    border-right: none;
                    padding: 15px;
                }}
                .content {{
                    margin-left: 0;
                    padding: 15px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="nav-pane">
            <h2>Table of Contents</h2>
            <ul>
                {nav_links}
            </ul>
        </div>
        <div class="content">
            <h1>Comprehensive Neuropsychological Evaluation</h1>
            <h2>(Confidential)</h2>
            {patient_info_html}
            {html_sections}
        </div>

        <script>
            // Add smooth scroll behavior for section navigation
            document.querySelectorAll('.nav-link').forEach(link => {{
                link.addEventListener('click', function(e) {{
                    e.preventDefault();
                    const target = document.querySelector(link.getAttribute('href'));
                    window.scrollTo({{ top: target.offsetTop - 50, behavior: 'smooth' }});
                }});
            }});

            // Expand/collapse sections
            document.querySelectorAll('h2').forEach(h2 => {{
                h2.addEventListener('click', function() {{
                    const section = h2.closest('.content-section');
                    const pre = section.querySelector('pre');
                    if (pre.style.display === 'none') {{
                        pre.style.display = 'block';
                    }} else {{
                        pre.style.display = 'none';
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    """

    # Render with Jinja2
    template = Template(html_content)
    rendered_html = template.render(patient_info=patient_info)

    # Write rendered HTML to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    webbrowser.open(f"file://{os.path.abspath(output_file)}")

