from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import numpy as np
import faiss
from app.faiss.faiss_index import save_faiss_index, load_or_create_faiss

embedding_model = OpenAIEmbeddings()

def store_paper_in_faiss(faiss_index, paper_id: str, paper_text: str):
    """Chunks extracted text and stores embeddings in FAISS with paper_id metadata using batch processing."""
    
    faiss_index = load_or_create_faiss()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=75)
    chunks = text_splitter.split_text(paper_text)

    # 🔹 Batch embedding for better efficiency
    chunk_embeddings = embedding_model.embed_documents(chunks)  # 🔥 Uses batch processing

    if faiss_index.ntotal == 0:
        faiss_index = faiss.IndexFlatL2(len(chunk_embeddings[0]))
        faiss_index.paper_ids = []

    faiss_index.paper_ids.extend([paper_id] * len(chunks))
    faiss_index.add(np.array(chunk_embeddings, dtype=np.float32))

    save_faiss_index(faiss_index)
