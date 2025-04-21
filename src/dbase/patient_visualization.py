import pdb
import json
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.feature_selection import VarianceThreshold
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from umap import UMAP
import matplotlib.pyplot as plt
import seaborn as sns

# --- Step 1: Load and Flatten JSON ---
def load_data(file_path):
    with open(file_path, 'r') as f:
        raw_data = json.load(f)
    flat_data = []
    for patient in raw_data:
        flat_row = pd.json_normalize(patient['mapped_data'], sep='__')
        flat_row['patient_id'] = patient['patient_id']
        flat_data.append(flat_row)
    df = pd.concat(flat_data, ignore_index=True)
    return df

# --- Step 2: Preprocess Data ---
def preprocess(df):
    df = df.drop(columns=['patient_id'])
    df = df.fillna(0)

    # One-hot encode categorical and binary fields
    df_encoded = pd.get_dummies(df)

    # Drop near-constant features
    selector = VarianceThreshold(threshold=0.01)
    df_reduced = selector.fit_transform(df_encoded)
    reduced_columns = df_encoded.columns[selector.get_support()]
    df_reduced = pd.DataFrame(df_reduced, columns=reduced_columns)

    return df_reduced, df_encoded.columns

# --- Step 3: PCA + UMAP ---
def run_dimensionality_reduction(df_encoded):
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(df_encoded)

    umap_model = UMAP(n_components=2, random_state=42)
    umap_result = umap_model.fit_transform(df_encoded)

    return pca_result, umap_result, pca

# --- Step 4: Visualize ---
def plot_embeddings(pca_result, umap_result):
    fig, ax = plt.subplots(1, 2, figsize=(14, 6))

    ax[0].scatter(pca_result[:, 0], pca_result[:, 1], alpha=0.6)
    ax[0].set_title("PCA of Patients")
    ax[0].set_xlabel("PC1")
    ax[0].set_ylabel("PC2")

    ax[1].scatter(umap_result[:, 0], umap_result[:, 1], alpha=0.6)
    ax[1].set_title("UMAP of Patients")
    ax[1].set_xlabel("UMAP 1")
    ax[1].set_ylabel("UMAP 2")

    plt.tight_layout()
    plt.show()

# --- Step 5: Show Important Features ---
def show_top_pca_features(pca, feature_names, top_n=20):
    pc1_loadings = pd.Series(np.abs(pca.components_[0]), index=feature_names)
    pc2_loadings = pd.Series(np.abs(pca.components_[1]), index=feature_names)

    print("\nTop contributing features to PC1:")
    print(pc1_loadings.sort_values(ascending=False).head(top_n))

    print("\nTop contributing features to PC2:")
    print(pc2_loadings.sort_values(ascending=False).head(top_n))

# --- Main ---
if __name__ == "__main__":
    path_to_json = "./output/all_patients_mapped.json"  # Change this to your file path

    print("🔄 Loading and flattening data...")
    df = load_data(path_to_json)

    print("⚙️ Preprocessing...")
    df_processed, feature_names = preprocess(df)

    # ---------------------------------------------------------------
    # Find the overlap in the active features between two patients.
    # ---------------------------------------------------------------
    a = df.iloc[0].astype(bool)
    b = df.iloc[1].astype(bool)

    intersection = (a & b).sum()
    union = (a | b).sum()
    jaccard = intersection / union

    print(f"Jaccard similarity: {jaccard:.3f}")
    
    from sklearn.metrics import pairwise_distances
    import seaborn as sns

    binary_matrix = df.astype(bool).astype(int).values
    distances = pairwise_distances(binary_matrix, metric='jaccard')
    similarities = 1 - distances

    sns.heatmap(similarities, cmap="viridis")
    plt.title("Patient Similarity (Jaccard)")
    plt.show()
    
    # ---------------------------------------------------------------
    pdb.set_trace()
    
    # print("📉 Running PCA and UMAP...")
    # pca_result, umap_result, pca = run_dimensionality_reduction(df_processed)

    # print("📊 Plotting results...")
    # plot_embeddings(pca_result, umap_result)

    # print("🔍 Showing top PCA features...")
    # show_top_pca_features(pca, df_processed.columns)
