import os
import pdb
import plotly.graph_objects as go
from plotly.io import to_html
import plotly.colors as pc
import webbrowser

def create_graph(data, structured_data, html_table, output_file='output.html'):
    # Build the plotting order (subscales + main group header at the end of each group)
    plot_order = []
    group_boundaries = []
    group_labels = []
    group_indices = []

    x = 0
    for group, subscales in structured_data.items():
        group_boundaries.append(x - 0.5)
        plot_order.extend(subscales)
        x += len(subscales)
        group_indices.append(x)
        plot_order.append(group)
        group_boundaries.append(x + 0.5)
        group_labels.append(x - len(subscales) / 2)
        x += 1

    x_positions = list(range(len(plot_order)))
    y_values = [int(data[label]) for label in plot_order]

    adaptive_index = plot_order.index('Behavioral Symptoms Index') + 1

    fig = go.Figure()

    # Plot 1: Before Adaptive
    fig.add_trace(go.Scatter(
        x=x_positions[0:adaptive_index],
        y=y_values[0:adaptive_index],
        mode='lines+markers',
        name='Behavioral Scales',
        marker=dict(color='blue'),
        line=dict(color='blue')
    ))

    # Plot 2: After Adaptive
    fig.add_trace(go.Scatter(
        x=x_positions[adaptive_index:],
        y=y_values[adaptive_index:],
        mode='lines+markers',
        name='Adaptive Scales',
        marker=dict(color='blue'),
        line=dict(color='blue')
    ))

    # Add vertical group boundary lines
    for boundary in group_boundaries:
        fig.add_vline(x=boundary, line_width=1, line_dash="dash", line_color="lightgray")

    # Thick line for adaptive boundary
    fig.add_vline(x=adaptive_index - 0.5, line_width=3, line_color="black")

    # Add shaded areas
    total_len = len(plot_order)
    fig.add_shape(type="rect", x0=0, x1=adaptive_index - 0.5, y0=60, y1=70, fillcolor="gray", opacity=0.3, line_width=0)
    fig.add_annotation(x=adaptive_index / 2, y=65, text="AT-RISK", showarrow=False, font=dict(size=12, color="gray"))

    fig.add_shape(type="rect", x0=0, x1=adaptive_index - 0.5, y0=70, y1=120, fillcolor="gray", opacity=0.5, line_width=0)
    fig.add_annotation(x=adaptive_index / 2, y=95, text="CLINICALLY SIGNIFICANT", showarrow=False, font=dict(size=12, color="gray"))

    fig.add_shape(type="rect", x0=adaptive_index - 0.5, x1=total_len, y0=30, y1=40, fillcolor="gray", opacity=0.3, line_width=0)
    fig.add_annotation(x=adaptive_index + (total_len - adaptive_index)/2, y=35, text="AT-RISK", showarrow=False, font=dict(size=12, color="gray"))

    fig.add_shape(type="rect", x0=adaptive_index - 0.5, x1=total_len, y0=0, y1=30, fillcolor="gray", opacity=0.5, line_width=0)
    fig.add_annotation(x=adaptive_index + (total_len - adaptive_index)/2, y=15, text="CLINICALLY SIGNIFICANT", showarrow=False, font=dict(size=12, color="gray"))

    # X-tick labels
    x_labels = plot_order
    fig.update_xaxes(
        tickvals=x_positions,
        ticktext=x_labels,
        tickangle=45
    )

    # Group headers (above plot)
    for idx, group in enumerate(structured_data.keys()):
        fig.add_annotation(
            x=group_labels[idx], y=130,
            text=f"<b>{group}</b>", showarrow=False,
            font=dict(size=10)
        )

    fig.update_layout(
        title="Clinical and Adaptive T Score Profile",
        yaxis_title="Score",
        yaxis=dict(range=[0, 140], gridcolor="lightgray", dtick=10),
        margin=dict(l=40, r=40, t=40, b=120),
        plot_bgcolor="white",
        height=500        
    )

    # Step 2: Convert the Plotly figure to HTML
    fig_html = to_html(fig, include_plotlyjs='cdn', full_html=False)

    # Step 3: Combine the table + the plot
    full_html = f"""
    <html>
    <head>
        <title>BASC-3 Report</title>
        <meta charset="utf-8">
    </head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f9f9f9;
        }}

        .container {{
            width: 90%;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            margin-bottom: 20px;
        }}

        th, td {{
            padding: 10px;
            text-align: center;
        }}

        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}

        td {{
            background-color: #fff;
        }}

        .highlight {{
            background-color: orange;
            color: white;
        }}

        .adaptive-skill {{
            background-color: lightblue;
            color: black;
        }}

        hr {{
            border: 1px solid #ddd;
        }}

        /* Responsive Design */
        @media (max-width: 768px) {{
            table, th, td {{
                font-size: 12px;
            }}
            .container {{
                width: 100%;
                padding: 15px;
            }}
        }}

        /* Plotly chart styling */
        .plot-container {{
            text-align: center;
            margin-top: 20px;
        }}
    </style>
    <body>
        <div class="container">
            {html_table}
            <hr>
            <div class="plot-container">
                {fig_html}
            </div>
        </div>
    </body>
    </html>
    """

    # Step 4: Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_html)

    print(f"HTML report saved to: {output_file}")


def create_combined_graph(all_data, structured_data, html_table, output_file='output.html'):
    plot_order = []
    group_boundaries = []
    group_labels = []
    x = 0
    
    for group, subscales in structured_data.items():
        group_boundaries.append(x - 0.5)
        plot_order.extend(subscales)
        x += len(subscales)
        plot_order.append(group)  # composite score
        group_boundaries.append(x + 0.5)
        group_labels.append(x - len(subscales) / 2)
        x += 1
            
    x_positions = list(range(len(plot_order)))
    adaptive_index = plot_order.index('Behavioral Symptoms Index') + 1 if 'Behavioral Symptoms Index' in plot_order else len(plot_order) // 2
    total_len = len(plot_order)

    fig = go.Figure()
    colors = pc.qualitative.Plotly

    for i, (pdf_name, data) in enumerate(all_data.items()):
        rater_label = data.get('rater_label', 'Unknown')

        # Handle missing or non-numeric data gracefully
        y_values = []
        normalized_data = {k.strip().lower(): v for k, v in data['data'].items()}
        for label in plot_order:
            normalized_label = label.strip().lower()
            val = normalized_data.get(normalized_label, None)

            # print(f"Looking for '{normalized_label}' → found: {val}")  # Debug line

            if val is None or (isinstance(val, str) and not val.strip().isdigit()):
                y_values.append(None)
            else:
                try:
                    y_values.append(int(val))
                except (ValueError, TypeError):
                    y_values.append(None)

        color = colors[i % len(colors)]
        group_id = f"group_{i}"
        # pdb.set_trace()
        # Left half (External/Internal)
        fig.add_trace(go.Scatter(
            x=x_positions[0:adaptive_index],
            y=y_values[0:adaptive_index],
            mode='lines+markers',
            name=rater_label,
            line=dict(color=color),
            marker=dict(color=color),
            showlegend=True,
            legendgroup=group_id
        ))

        # Right half (Adaptive)
        fig.add_trace(go.Scatter(
            x=x_positions[adaptive_index:],
            y=y_values[adaptive_index:],
            mode='lines+markers',
            name=pdf_name,
            line=dict(color=color),
            marker=dict(color=color),
            showlegend=False,
            legendgroup=group_id
        ))

    # Add visual regions and annotations
    for boundary in group_boundaries:
        fig.add_vline(x=boundary, line_width=1, line_dash="dash", line_color="lightgray")

    fig.add_vline(x=adaptive_index - 0.5, line_width=3, line_color="black")

    fig.add_shape(type="rect", x0=0, x1=adaptive_index - 0.5, y0=60, y1=70, fillcolor="gray", opacity=0.3, line_width=0)
    fig.add_annotation(x=adaptive_index / 2, y=65, text="AT-RISK", showarrow=False)

    fig.add_shape(type="rect", x0=0, x1=adaptive_index - 0.5, y0=70, y1=120, fillcolor="gray", opacity=0.5, line_width=0)
    fig.add_annotation(x=adaptive_index / 2, y=95, text="CLINICALLY SIGNIFICANT", showarrow=False)

    fig.add_shape(type="rect", x0=adaptive_index - 0.5, x1=total_len, y0=30, y1=40, fillcolor="gray", opacity=0.3, line_width=0)
    fig.add_annotation(x=adaptive_index + (total_len - adaptive_index)/2, y=35, text="AT-RISK", showarrow=False)

    fig.add_shape(type="rect", x0=adaptive_index - 0.5, x1=total_len, y0=0, y1=30, fillcolor="gray", opacity=0.5, line_width=0)
    fig.add_annotation(x=adaptive_index + (total_len - adaptive_index)/2, y=15, text="CLINICALLY SIGNIFICANT", showarrow=False)

    fig.update_xaxes(tickvals=x_positions, ticktext=plot_order, tickangle=45)
    for idx, group in enumerate(structured_data.keys()):
        fig.add_annotation(x=group_labels[idx], y=130, text=f"<b>{group}</b>", showarrow=False)

    fig.update_layout(
        title="Clinical and Adaptive T Score Profile",
        yaxis_title="T Score",
        yaxis=dict(range=[0, 140], dtick=10, gridcolor="lightgray"),
        height=500,
        plot_bgcolor="white",
    )

    fig_html = to_html(fig, include_plotlyjs='cdn', full_html=False)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"""
        <html>
        <head>
            <title>Combined BASC Report</title>
        </head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f9f9f9;
            }}
            .container {{
                width: 90%;
                margin: 0 auto;
                padding: 20px;
                background-color: white;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 14px;
                margin-bottom: 20px;
            }}
            th, td {{
                padding: 10px;
                text-align: center;
            }}
            th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            td {{
                background-color: #fff;
            }}
            .highlight {{
                background-color: orange;
                color: white;
            }}
            .adaptive-skill {{
                background-color: lightblue;
                color: black;
            }}
            hr {{
                border: 1px solid #ddd;
            }}
            @media (max-width: 768px) {{
                table, th, td {{
                    font-size: 12px;
                }}
                .container {{
                    width: 100%;
                    padding: 15px;
                }}
            }}
            .plot-container {{
                text-align: center;
                margin-top: 20px;
            }}
        </style>
        <body>
        <div class="container">
            {html_table}
            <hr>
            <div class="plot-container">{fig_html}</div>
        </div>
        </body>
        </html>
        """)

    report_file = os.path.abspath(output_file)
    print(f"Saved combined HTML to: {report_file}")
    webbrowser.open(f"file://{report_file}")