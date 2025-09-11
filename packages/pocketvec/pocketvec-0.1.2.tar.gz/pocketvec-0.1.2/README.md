# PocketVec 🗂️✨🧠

 PocketVec is a lightweight vector store designed for small to medium datasets. It allows you to efficiently create    embeddings for a list of text chunks and retrieve the most similar chunks using either cosine similarity or Euclidean distance.

 PocketVec is ideal for users who want a fast and easy-to-use solution without needing heavy infrastructure or databases.

# Quick Workflow Overview  ⚡🔄

 Texts → [Create embeddings] → [Retrieve similar chunks] → Results
 
         OR
         
 Texts → [Create & Save embeddings] → [Load embeddings + Data] → [Retrieve similar chunks] → Results

# Features  ✅🚀

 Lightweight & fast: Optimized for smaller datasets without external dependencies beyond sentence-transformers.

 Flexible workflows:

 Immediate use – create embeddings and retrieve related text chunks in one go, storing everything in memory.

 Persistent embeddings – create embeddings, save them to a file, and reuse them later with the corresponding data chunks.

 Similarity methods: Cosine similarity and Euclidean distance.

 Easy integration: Works with any Python project with simple function calls.

# How it works  🛠️🔍

 Input: Provide your dataset as a list of text chunks.

 Embedding: PocketVec generates embeddings for the texts using a HuggingFace sentence transformer.

 Retrieve: Query the vector store to find the most similar chunks to your input query.

 Optional persistence: Save embeddings for later use and reuse them with the original data chunks.

# Recommended Usage 📝💡

 PocketVec supports two main workflows:

 One-step embeddings and retrieval

 Create embeddings for your data chunks.

 Retrieve the top N most similar chunks to your query.

 Separate creation and retrieval

 Generate embeddings and save them to a file.

 Later, load the embeddings and provide the original data chunks to perform retrieval.

# Similarity Metrics 📐🔢

 PocketVec supports the following similarity/distance metrics:

 Cosine similarity – measures angular similarity between vectors.

 Euclidean distance – measures straight-line distance between vectors in space.

# Examples 💻📂

 For detailed usage, check the provided examples:

 Basic workflow: Creating embeddings and retrieving related chunks in one go → examples/demo_basic.py

 Persistent workflow: Saving embeddings and using them later → examples/demo_with_file.py

# Installation 💾⚙️

 Install PocketVec via pip:

 pip install pocketvec
 
 Dependencies

 Python 3.8+

 numpy

 sentence-transformers

 huggingface-hub

 (These will be installed automatically when using pip.)

# License 📜🔓

  PocketVec is released under the MIT License.



