from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict, Counter
import numpy as np
import pdb

# Load sentence transformer model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def extract_provider(file_name):
    base = file_name.replace(".json", "")
    if "_" in base:
        return base.split("_")[0]  # everything before the first underscore
    else:
        return base.split(" ")[0]  # otherwise, first word
    
def generate_common_recommendations(recommendation_data, eps=0.2, min_samples=2):
    recs = [(entry['file'], entry['recommendation'].strip()) for entry in recommendation_data]
    texts = [r[1] for r in recs]
    files = [r[0] for r in recs]

    print(f"Loaded {len(recs)} total recommendations from {len(set(files))} files.")

    # Get sentence embeddings
    embeddings = model.encode(texts, normalize_embeddings=True)

    # Compute distance matrix
    distance_matrix = 1 - cosine_similarity(embeddings)
    distance_matrix = np.clip(distance_matrix, 0, 1)

    # Cluster using DBSCAN
    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='precomputed')
    labels = clustering.fit_predict(distance_matrix)
    noise_points = np.sum(labels == -1)
    print(f"\nClustering complete. Noise points: {noise_points}")

    # Collect clusters
    clusters = defaultdict(list)
    for idx, label in enumerate(labels):
        if label != -1:
            clusters[label].append({
                'file': files[idx],
                'text': texts[idx],
                'embedding': embeddings[idx]
            })

    output_file = "clusters_output.txt"

    with open(output_file, "w", encoding="utf-8") as f:
    # Print clusters with provider overlap
        if clusters:
            f.write("\n=== Semantic Clusters of Recommendations ===\n")
            for cluster_id, members in clusters.items():
                provider_count = Counter([extract_provider(m['file']) for m in members])
                providers_present = list(provider_count.keys())
                is_common = len(providers_present) == 3  # adjust if you have more/less providers

                # Find most central sentence
                cluster_embeddings = np.array([m['embedding'] for m in members])
                centroid = cluster_embeddings.mean(axis=0)
                central_idx = np.argmin(np.linalg.norm(cluster_embeddings - centroid, axis=1))
                central_text = members[central_idx]['text']

                f.write(f"\n-- Cluster {cluster_id} -- {'[COMMON]' if is_common else ''}\n")
                f.write(f"Representative: {central_text}\n")
                f.write(f"Providers in cluster: {providers_present}\n")
                for m in members:
                    f.write(f"  [{m['file']}] {m['text']}\n")
        else:
            f.write("No meaningful clusters found.\n")

    return clusters

import json
with open('recommendations.json', 'r', encoding='utf-8') as f:
    recommendation_data = json.load(f)

clusters= generate_common_recommendations(recommendation_data)
# pdb.set_trace()