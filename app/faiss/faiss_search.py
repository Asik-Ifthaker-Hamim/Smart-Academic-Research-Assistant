import faiss
import numpy as np
from app.faiss.faiss_index import load_or_create_faiss

def search_faiss(faiss_index, query_embedding, k=5):
    """Search FAISS for the most relevant documents."""
    
    # 🔹 Reload FAISS index to ensure data is loaded
    faiss_index = load_or_create_faiss() 

    if faiss_index.ntotal == 0:
        print("Debug: FAISS index is empty. No documents to retrieve.")
        return []

    print(f"📌 Debug: Querying FAISS with k={k} (FAISS total vectors: {faiss_index.ntotal})")

    query_vector = np.array([query_embedding], dtype=np.float32)
    distances, indices = faiss_index.search(query_vector, k)

    print(f"Debug: FAISS returned indices: {indices}")

    return indices[0].tolist()
