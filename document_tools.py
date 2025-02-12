import easyocr
import streamlit as st
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from utils import get_openai_api_key
from langchain.text_splitter import RecursiveCharacterTextSplitter

ocr_reader = easyocr.Reader(['en'])  

def extract_text_with_ocr(image_path):
    """Extracts text from an image using EasyOCR."""
    try:
        results = ocr_reader.readtext(image_path)
        extracted_text = " ".join([text for box, text, prob in results])  
        return extracted_text
    except Exception as e:
        st.error(f"OCR Error: {e}")
        return ""

@st.cache_resource
def load_and_index_pdf(file_path):
    try:
        loader = PyMuPDFLoader(file_path)
        documents = loader.load()
        if not documents or not documents[0].page_content.strip():
            st.warning("PDF content is empty or not text-based. Trying OCR...")  
            import fitz  
            doc = fitz.open(file_path)  
            all_text = ""
            for page in doc: 
                img = page.get_pixmap()  
                img_path = "temp_img.png"  
                img.save(img_path)
                extracted_text = extract_text_with_ocr(img_path)
                all_text += extracted_text

            if not all_text:
                st.error("OCR could not extract text either.")
                return None

            
            from langchain.docstore.document import Document
            documents = [Document(page_content=all_text)]

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