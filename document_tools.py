from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from utils import get_openai_api_key
import streamlit as st

@st.cache_resource
def load_and_index_pdf(file_path):
    try:
        loader = PyMuPDFLoader(file_path)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=75)
        texts = text_splitter.split_documents(documents)

        embeddings = OpenAIEmbeddings(openai_api_key=get_openai_api_key())
        db = FAISS.from_documents(texts, embeddings)
        return db
    except Exception as e:
        st.error(f"Error loading and indexing PDF: {e}")
        return None

def query_indexed_pdf(db, query):
    if db:
        docs = db.similarity_search(query)
        return "\n\n".join([doc.page_content for doc in docs])
    else:
        return "No document loaded or indexing failed."