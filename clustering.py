import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# Limit to 1 thread for reproducibility/performance on smaller machines
faiss.omp_set_num_threads(1)

# === Load Articles ===
with open("data/articles.json", "r") as infile:
    articles = json.load(infile)

titles = [a["title"] for a in articles]
contents = [a.get("text", "") for a in articles]

# === Encode with Sentence-BERT ===
model = SentenceTransformer("all-MiniLM-L6-v2")
title_embeddings = model.encode(titles, convert_to_numpy=True, normalize_embeddings=True)
content_embeddings = model.encode(contents, convert_to_numpy=True, normalize_embeddings=True)

# === Compute Combined Similarity Matrix ===
def compute_combined_similarity(title_embeds, content_embeds, has_content_mask):
    title_sim = title_embeds @ title_embeds.T
    content_sim = content_embeds @ content_embeds.T
    combined_sim = np.where(
        has_content_mask[:, None] & has_content_mask[None, :],
        np.maximum(title_sim, content_sim),
        title_sim,
    )
    return combined_sim

has_content = np.array([bool(c.strip()) for c in contents])
similarity_matrix = compute_combined_similarity(title_embeddings, content_embeddings, has_content)

# === Greedy Clustering Based on Similarity Threshold ===
threshold = 0.75
n = len(articles)
visited = [False] * n
clusters = []

for i in range(n):
    if visited[i]:
        continue
    cluster = [i]
    visited[i] = True
    for j in range(n):
        if not visited[j] and similarity_matrix[i][j] >= threshold:
            cluster.append(j)
            visited[j] = True
    clusters.append(cluster)

# === Assign Cluster IDs ===
for cluster_id, cluster in enumerate(clusters):
    for idx in cluster:
        articles[idx]["cluster_id"] = cluster_id

# === Save Clustered Articles ===
with open("data/articles_clustered.json", "w") as outfile:
    json.dump(articles, outfile, indent=2)

print(f"Done. {len(clusters)} clusters written to data/articles_clustered.json")
