import re
import numpy as np
import pandas as pd
from collections import defaultdict
from sentence_transformers import SentenceTransformer
from sklearn.manifold import TSNE
from sklearn.preprocessing import MinMaxScaler
import plotly.express as px
import pdb

def extract_provider(file_name):
    base = file_name.replace(".json", "")
    if "_" in base:
        return base.split("_")[0]  # everything before the first underscore
    else:
        return base.split(" ")[0]  # otherwise, first word
    
def clean_text(t):
    """More thorough text cleaning function"""
    if t is None:
        return ""
    if not isinstance(t, str):
        t = str(t)
    # Remove null bytes, replacement chars, and newlines
    t = t.replace('\x00', '').replace('�', '').replace('\n', ' ')
    # Remove any other control characters
    t = ''.join(c for c in t if ord(c) >= 32 or c == '\t')
    return t.strip()

# Load your file with proper error handling
try:
    with open("clusters_output.txt", "r", encoding="utf-8", errors="replace") as file:
        text = file.read()
except Exception as e:
    print(f"Error reading file: {e}")
    exit(1)

# Parse clusters with better error handling
clusters = []
for cluster_text in text.strip().split('-- Cluster ')[1:]:
    try:
        lines = cluster_text.strip().splitlines()
        if not lines:
            continue
            
        cluster_id = int(clean_text(lines[0].split(' --')[0].strip()))
        
        if len(lines) < 3:
            print(f"Skipping cluster {cluster_id} due to insufficient data")
            continue
            
        rep_text = clean_text(lines[1].replace('Representative: ', '').strip())
        
        # Safer evaluation of provider line
        provider_line_raw = clean_text(lines[2].replace('Providers in cluster: ', '').strip())
        try:
            provider_line = eval(provider_line_raw)
            provider_line = [clean_text(p) for p in provider_line]
        except:
            print(f"Error parsing provider line in cluster {cluster_id}, using empty list")
            provider_line = []
        
        rec_lines = lines[3:]
        
        recs_by_provider = defaultdict(int)
        for line in rec_lines:
            line = clean_text(line.strip())
            match = re.match(r"\[(.*?)\]", line)
            if match:
                raw = match.group(1)
                provider = clean_text(raw.split("_")[0] if "_" in raw else raw.split(" ")[0])
                recs_by_provider[provider] += 1
        
        clusters.append({
            'id': cluster_id,
            'representative': rep_text,
            'providers': provider_line,
            'recommendations': {clean_text(k): v for k, v in recs_by_provider.items()}
        })
    except Exception as e:
        print(f"Error processing cluster: {e}")
        continue

# Filter clusters with >1 unique provider
filtered_clusters = [c for c in clusters if len(set(c['providers'])) > 1]
print(f"Found {len(filtered_clusters)} clusters with multiple providers")
# pdb.set_trace()
# Compute embeddings
try:
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    representative_texts = [c['representative'] for c in filtered_clusters]
    embeddings = model.encode(representative_texts)
except Exception as e:
    print(f"Error computing embeddings: {e}")
    exit(1)

# t-SNE projection
try:
    tsne = TSNE(n_components=2, random_state=42, perplexity=min(5, len(filtered_clusters)-1) if len(filtered_clusters) > 1 else 1)
    rep_2d = tsne.fit_transform(embeddings)
    rep_2d_scaled = MinMaxScaler().fit_transform(rep_2d)
except Exception as e:
    print(f"Error in t-SNE projection: {e}")
    exit(1)

# Create a DataFrame directly instead of building dictionary first
plot_data = []
# pdb.set_trace()
for i, cluster in enumerate(filtered_clusters):
    cx, cy = rep_2d_scaled[i]
    cluster_id = cluster['id']
    
    # Add cluster center
    plot_data.append({
        "x": float(cx),
        "y": float(cy),
        "label": f"Cluster {cluster_id}",
        "provider": "center",
        "count": 0,
        "type": "Cluster Center",
        "cluster": f"Cluster {cluster_id}",
        "text": clean_text(cluster['representative'])
    })
    
    # Add providers
    for provider, count in cluster['recommendations'].items():
        offset_x = float(np.random.uniform(-0.02, 0.02))
        offset_y = float(np.random.uniform(-0.02, 0.02))
        plot_data.append({
            "x": float(cx + offset_x),
            "y": float(cy + offset_y),
            "label": clean_text(cluster['representative']),
            "provider": clean_text(provider),
            "count": int(count),
            "type": "Provider",
            "cluster": f"Cluster {cluster_id}",
            "text": f"{clean_text(provider)} ({count} recommendations)"
        })

# Convert to DataFrame
try:
    # Ensure all string values are clean
    df = pd.DataFrame(plot_data)
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(clean_text)
    
    print(f"Created DataFrame with {len(df)} rows")
    
    # Check for null bytes in the DataFrame
    for col in df.columns:
        if df[col].dtype == object:  # Only check string columns
            has_null = df[col].str.contains('\x00', na=False).any()
            if has_null:
                print(f"Warning: Column {col} still contains null bytes. Cleaning again.")
                df[col] = df[col].apply(lambda x: clean_text(x))
except Exception as e:
    print(f"Error creating DataFrame: {e}")
    exit(1)

# -------------------------------------------------
# Common Recommendations Clustered by Providers
# -------------------------------------------------

import plotly.graph_objects as go
import plotly.express as px

# Generate distinct colors for each cluster using Plotly's color sequence
cluster_ids = [cluster['id'] for cluster in filtered_clusters]
color_sequence = px.colors.qualitative.Plotly
cluster_colors = {
    cluster_id: color_sequence[i % len(color_sequence)]
    for i, cluster_id in enumerate(cluster_ids)
}

import matplotlib.colors as mcolors  # for hex to rgba conversion

# Convert cluster colors to translucent RGBA
cluster_colors_rgba = {
    cluster_id: mcolors.to_rgba(color, alpha=0.7)
    for cluster_id, color in cluster_colors.items()
}

# Format back to rgba strings for Plotly
cluster_colors_rgba = {
    k: f'rgba({int(r*255)}, {int(g*255)}, {int(b*255)}, {a})'
    for k, (r, g, b, a) in cluster_colors_rgba.items()
}

# Create the figure
fig = go.Figure()

# Extract base provider names from all clusters
base_provider_names = sorted({
    re.split(r'\s+', p.strip())[0]  # Take the first word
    for c in filtered_clusters
    for p in c['providers']
})

# Assign a unique color to each base provider name
provider_palette = px.colors.qualitative.Bold  # or px.colors.qualitative.Set3
provider_colors = {
    base_name: color
    for base_name, color in zip(base_provider_names, provider_palette)
}

# Add clusters and their providers
for i, cluster in enumerate(filtered_clusters):
    cx, cy = rep_2d_scaled[i]
    cluster_id = cluster['id']
    color = cluster_colors_rgba[cluster_id]
    
    # Add cluster center point
    fig.add_trace(go.Scatter(
        x=[cx],
        y=[cy],
        mode='markers',
        marker=dict(
            size=14,
            color=color,
            line=dict(width=3, color='black'),
            symbol='circle'
        ),
        name=f"Cluster {cluster_id} Center",
        legendgroup=f"Cluster {cluster_id}",
        hoverinfo='text',
        hovertext=[f"Cluster {cluster_id} - Representative: {cluster['representative']}"]
    ))

    # Add provider points
    for provider, count in cluster['recommendations'].items():
        # Extract base name of provider
        base_name = re.split(r'\s+', provider)[0]
        outline_color = provider_colors.get(base_name, 'gray')

        offset_x = float(np.random.uniform(-0.02, 0.02))
        offset_y = float(np.random.uniform(-0.02, 0.02))
        fig.add_trace(go.Scatter(
            x=[cx + offset_x],
            y=[cy + offset_y],
            mode='markers',
            marker=dict(
                size=8 + count,
                color=color,  # Fill = cluster color
                symbol='circle',
                line=dict(
                    width=2,
                    color=outline_color  # Outline = provider color
                )
            ),
            name=f"Provider - {base_name}",
            legendgroup=f"Cluster {cluster_id}",
            showlegend=False,  # Hide duplicate legend entries for providers
            hoverinfo='text',
            hovertext=[f"{provider} ({count} recommendations)"]
        ))

# Layout customization
fig.update_layout(
    title="Interactive Cluster Visualization with Cluster Centers",
    xaxis_title="X",
    yaxis_title="Y",
    legend_title="Cluster",
    template="plotly_white",
    showlegend=True
)

fig.show()

# -------------------------------------------------
# Common Recommendations Across Providers (Bar Chart)
# -------------------------------------------------
for cluster in filtered_clusters:
    print(f"Cluster {cluster['id']} - Representative: {cluster['representative']}")
    for provider, count in cluster['recommendations'].items():
        print(f"  Provider: {provider} - Recommendations: {count}")

data = []
for cluster in filtered_clusters:
    rep = cluster['representative']
    for provider, count in cluster['recommendations'].items():
        data.append({'Representative': rep, 'Provider': provider, 'Recommendations': count})

df = pd.DataFrame(data)

# Create the grouped bar chart
fig = px.bar(df, x='Representative', y='Recommendations', color='Provider', barmode='group')

fig.update_layout(
    xaxis=dict(
        showticklabels=False  # Hides the labels
    )
)

fig.show()

# -------------------------------------------------
# Common Recommendations Per Provider
# -------------------------------------------------
data = []
for cluster in filtered_clusters:
    rep = cluster['representative']
    for provider, count in cluster['recommendations'].items():
        data.append({
            'Provider': provider,
            'Recommendation': rep,
            'Count': count  # Or set to 1 if you only want presence
        })

df = pd.DataFrame(data)

fig = px.bar(
    df,
    x='Provider',
    y='Count',
    color='Recommendation',  # Grouped bars per provider
    barmode='group',
    title="Common Recommendations per Provider"
)

fig.update_layout(
    xaxis_title="Provider",
    yaxis_title="Number of Common Recommendations"
)

fig.show()