import numpy as np
from sentence_transformers import SentenceTransformer
from huggingface_hub import login

from .similarity import calculate_cosine_similarity, calculate_euclidean_distance
from .io_utils import read_embeddings, save_embeddings_to_file


class PocketVec:
    def __init__(self, hf_token, model_name):
        self.load_model = SentenceTransformer(f'sentence-transformers/{model_name}')
        self.embeddings = None
        self.texts = None
        login(token=hf_token)

    def generate_embeddings(self, texts: list) -> None:

        #   *****************************************************
        #   Method to generate embeddings for given list of texts
        #   ******************************************************

        try : 
            print("Started Creating Embeddings...")
            self.texts = texts
            self.embeddings = self.load_model.encode(texts)
            print("Embeddings created Successfully")
        except Exception as e:
            print(f"Error when generating embeddings : {e}")

    def clear_embeddings(self) -> None:

        #  **********************************
        #  Method to clear embeddings created
        #  **********************************

        self.embeddings = None
        print("Cleared the Embeddings")

    def save_embeddings(self, file_name: str) -> None:
        save_embeddings_to_file(self.embeddings, file_name)

    def query_similar(self, query: str, similarity_type: str, no_of_results: int, file_path=None, texts=None):

        #  *****************************************************************
        #  Method to retrieve text chunks that are similar to the user query
        #  *****************************************************************


        if file_path is None:
            embeddings = self.embeddings
        else:
            embeddings = np.array(read_embeddings(file_path))

        if texts is None:
            texts = self.texts

        query_embedding = self.load_model.encode(query)

        if similarity_type == "cosine":
            return calculate_cosine_similarity(embeddings, query_embedding, no_of_results, texts)
        elif similarity_type == "euclidean":
            return calculate_euclidean_distance(embeddings, query_embedding, no_of_results, texts)
        else:
            raise ValueError(f"Unsupported similarity_type: {similarity_type}")
