import streamlit as st
import os
from dotenv import load_dotenv
from search_tools import google_search_with_pdf_links, arxiv_search
from document_tools import load_and_index_pdf, query_indexed_pdf
from summary_tools import summarize_text
from research_trends import analyze_research_trends  
from utils import get_openai_api_key
import arxiv
import tempfile
import time
from collections import Counter
from langchain_openai import ChatOpenAI

load_dotenv()

st.set_page_config(page_title="Academic Research Assistant", layout="wide")

st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox(
    "Choose the App mode",
    ["Search & Analyze", "Document Summary", "Research Trends", "Research Chat Assistant"], 
)
if 'faiss_db' not in st.session_state:
    st.session_state['faiss_db'] = None

if app_mode == "Search & Analyze":
    st.title("Search & Analyze Research Papers")

    search_query = st.text_input("Enter your research query (e.g., LLMs, cancer research):")

    if search_query:
        st.subheader("Google Search Results:")
        google_results = google_search_with_pdf_links(search_query)
        st.write(google_results)

        st.subheader("ArXiv Search Results:")
        arxiv_results = arxiv_search(search_query)
        st.write(arxiv_results)

elif app_mode == "Document Summary":
    st.title("Document Summary")

    uploaded_file = st.file_uploader("Upload a research paper (PDF)", type="pdf")

    if uploaded_file is not None:
        temp_filename = os.path.join("temp", uploaded_file.name)
        os.makedirs("temp", exist_ok=True)
        with open(temp_filename, "wb") as f:
            f.write(uploaded_file.read())

        st.success("File uploaded successfully!")

        user_query = st.text_input("Enter your query or summarization requirement (e.g., 'key findings in 50 words', 'research gaps'):", value="Summarize the key findings")
        word_limit = st.number_input("Enter the approximate word limit for the response:", min_value=20, max_value=200, value=100, step=10)

        if st.button("Get Results/Summary"):
            with st.spinner("Processing..."):
                faiss_db = load_and_index_pdf(temp_filename)

              
                results = query_indexed_pdf(faiss_db, user_query)

               
                summary = summarize_text(results, user_query=user_query, word_limit=word_limit)
            st.subheader("Result/Summary:")
            st.write(summary)
    else:
        st.info("Please upload a PDF file.")

elif app_mode == "Research Trends":
    st.title("Research Trends")

    time_range = st.selectbox("Select a time range:", ["Last Year", "Last 5 Years", "All Time"])
    search_query = st.text_input("Enter a search query (e.g., 'machine learning', 'cancer research'):", value="machine learning") #ADD

    if st.button("Generate Trends"):
        with st.spinner("Fetching and analyzing data..."):
            analyze_research_trends(time_range, search_query) 

elif app_mode == "Research Chat Assistant":
    st.title("Research Chat Assistant")
    st.write("Ask me questions about research, writing papers, and more!")

    user_question = st.text_input("Enter your question:")

    if user_question:
        with st.spinner("Thinking..."):
            try:
                llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7, openai_api_key=get_openai_api_key())
                response = llm.invoke(user_question)
                st.write(response.content)
            except Exception as e:
                st.error(f"An error occurred: {e}")