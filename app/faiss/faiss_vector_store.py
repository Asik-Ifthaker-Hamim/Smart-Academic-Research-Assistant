import os
from langchain.vectorstores import FAISS
from app.faiss.text_extraction import extract_text_from_file
from app.utils.text_processing import split_text_into_chunks
from typing import Union

def check_vectorstore_exists(file_id: str) -> bool:
    """Check if a vector store already exists for the given file UUID."""
    index_path = f"faiss_indexes/{file_id}.index"
    docstore_path = f"faiss_indexes/{file_id}.pkl"
    return os.path.exists(index_path) and os.path.exists(docstore_path)

def load_vector_store(file_id: str, embeddings) -> FAISS | None:
    """Load existing vector store if it exists."""
    if check_vectorstore_exists(file_id):
        try:
            return FAISS.load_local(f"faiss_indexes/{file_id}", embeddings)
        except Exception:
            return None
    return None

def save_vector_store(vectorstore: FAISS, file_id: str) -> None:
    """Save vector store to disk."""
    os.makedirs("faiss_indexes", exist_ok=True)
    vectorstore.save_local(f"faiss_indexes/{file_id}")

def get_or_create_vectorstore(file_id: str, file_path: str, embeddings) -> Union[FAISS, str]:
    """Get existing vector store or create new one using file UUID."""
    vectorstore = load_vector_store(file_id, embeddings)
    
    if vectorstore is None:
        extracted_text = extract_text_from_file(file_path)
        if extracted_text.startswith("Error"):
            return "Error: Could not process the document. Please ensure it's a valid PDF or TXT file."

        texts = split_text_into_chunks(extracted_text)
        vectorstore = FAISS.from_texts(texts, embeddings)
        save_vector_store(vectorstore, file_id)

    return vectorstore
