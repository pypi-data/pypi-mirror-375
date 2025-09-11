# similarity.py
import numpy as np


def calculate_cosine_similarity(embeddings, query_embedding, no_of_results, texts):
    print("Cosine Similarity Calculation in Progress...")
    try :
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

        cosine_similarities = np.dot(embeddings_norm, query_norm)
        sorted_indices = np.argsort(cosine_similarities)[-no_of_results:][::-1]

        print("Cosine Similarity calculation completed.")
        texts_np = np.array(texts)
    except Exception as e:
        return f"Exception ocurred while calculating cosine similarity : {e}"
    return dict(zip(
        texts_np[sorted_indices].tolist(),
        cosine_similarities[sorted_indices].tolist()
    ))


def calculate_euclidean_distance(embeddings, query_embedding, no_of_results, texts):
    try :
        euclidean_distances = np.linalg.norm(embeddings - query_embedding, axis=1)
        sorted_indices = np.argsort(euclidean_distances)[:no_of_results]

        print("Euclidean Distance calculation completed.")
        texts_np = np.array(texts)
    except Exception as e:
        return f"Exception ocurred while calculating euclidean distance : {e}"
    return dict(zip(
        texts_np[sorted_indices].tolist(),
        euclidean_distances[sorted_indices].tolist()
    ))
