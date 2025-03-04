import os
import faiss
import numpy as np
from app.core.config import settings

FAISS_INDEX_PATH = settings.FAISS_INDEX_PATH

def load_or_create_faiss():
    """Loads existing FAISS index or creates a new one if empty."""
    try:
        if os.path.exists(FAISS_INDEX_PATH):
            index = faiss.read_index(FAISS_INDEX_PATH)
            paper_ids_path = f"{FAISS_INDEX_PATH}_paper_ids.npy"
            index.paper_ids = list(np.load(paper_ids_path, allow_pickle=True)) if os.path.exists(paper_ids_path) else []  
        else:
            index = faiss.IndexFlatL2(1536)
            index.paper_ids = []

        if index.ntotal == 0:
            index = faiss.IndexFlatL2(1536)
            index.paper_ids = []

        return index
    except Exception as e:
        print(f"Error loading FAISS index: {str(e)}, creating a new one")
        index = faiss.IndexFlatL2(1536)
        index.paper_ids = []
        return index

def save_faiss_index(faiss_index):
    """Saves FAISS index efficiently without redundant writes."""
    if faiss_index.ntotal > 0:  # 🔹 Only save if there are stored vectors
        faiss.write_index(faiss_index, FAISS_INDEX_PATH)
        np.save(f"{FAISS_INDEX_PATH}_paper_ids.npy", np.array(faiss_index.paper_ids, dtype=object), allow_pickle=True)
