import json
import os
from pathlib import Path


def save_embeddings_to_file(embeddings, file_name: str):
    try :
        print(f"Saving embeddings to {file_name}...")
        folder = "embeddings"
        target_dir = Path(os.getcwd()) / folder
        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / file_name

        with open(file_path, "w", encoding="UTF-8") as f:
            json.dump(embeddings.tolist(), f)
        print("Embeddings saved successfully.")
    except Exception as e:
        print(f"Error while saving embeddings : {e}")


def read_embeddings(file_path):
    try :
        print(f"Reading embeddings from {file_path}...")
        with open(file_path, "r", encoding="UTF-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading embeddings from file : {e}")
