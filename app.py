import streamlit as st
import os
from dotenv import load_dotenv
from search_tools import arxiv_search, pubmed_search, scholarly_search
from document_tools import load_and_index_pdf, query_indexed_pdf
from summary_tools import summarize_text
from research_trends import analyze_research_trends
from utils import get_openai_api_key
import arxiv
import tempfile
import time
from collections import Counter
from langchain_openai import ChatOpenAI
import requests 

load_dotenv()

st.set_page_config(page_title="Academic Research Assistant", layout="wide")

st.sidebar.title("Features")
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
        st.subheader("PubMed Search Results:")
        pubmed_results = pubmed_search(search_query)
        st.write(pubmed_results)

        st.subheader("Scholarly Search Results:")
        scholarly_results = scholarly_search(search_query)
        st.write(scholarly_results)

        st.subheader("ArXiv Search Results:")
        arxiv_results = arxiv_search(search_query)

        if arxiv_results == "No results found on arXiv.":
            st.warning(arxiv_results)
        else:
           
            papers = []
            for paper_info in arxiv_results.strip().split("\n\n"):
                parts = paper_info.split("\n")
                paper_data = {}  

                for part in parts:
                  
                    split_part = part.split(": ", 1)
                    if len(split_part) == 2:  
                        key = split_part[0].strip()  
                        value = split_part[1].strip()  

                        paper_data[key] = value
                if "Title" in paper_data and "Authors" in paper_data and "Summary" in paper_data and "Link" in paper_data:
                    papers.append(paper_data)  

            if papers:
                selected_paper_title = st.selectbox("Select a paper to explore:", [paper["Title"] for paper in papers])

                selected_paper = next((paper for paper in papers if paper["Title"] == selected_paper_title), None)  
                if selected_paper:  
                    st.write(f"Authors: {selected_paper['Authors']}")  
                    st.write(f"Summary: {selected_paper['Summary']}")  
                    st.write(f"ArXiv Link: {selected_paper['Link']}")  

                    if selected_paper["Link"]: 
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
                            try:
                                response = requests.get(selected_paper["Link"])
                                response.raise_for_status()
                                tmpfile.write(response.content)
                                temp_pdf_path = tmpfile.name

                                
                                user_query = st.text_input("Ask a question about the selected paper (e.g., key findings, research gaps):",
                                                          value="Summarize the key findings")
                                word_limit = st.number_input("Enter the approximate word limit for the response:",
                                                            min_value=20, max_value=1000, value=100, step=10)

                                if st.button("Get Summary/Answer"):
                                    try:
                                        faiss_db = load_and_index_pdf(temp_pdf_path)

                                       
                                        results = query_indexed_pdf(faiss_db, user_query)

                                      
                                        summary = summarize_text(results, user_query=user_query, word_limit=word_limit)

                                        st.subheader("Summary/Answer:")
                                        st.write(summary)

                                    except Exception as e:
                                        st.error(f"An error occurred: {e}")
                            except requests.exceptions.RequestException as e:  
                                st.error(f"Error downloading PDF from ArXiv: {e}")

elif app_mode == "Document Summary":
    st.title("Document Summary")

    uploaded_file = st.file_uploader("Upload a research paper (PDF)", type="pdf")

    user_query = st.text_input("Enter your query or summarization requirement (e.g., 'key findings in 50 words', 'research gaps'):", value="Summarize the key findings")
    word_limit = st.number_input("Enter the approximate word limit for the response:", min_value=20, max_value=1000, value=100, step=10)
    text_upload = st.text_area("Or Paste your text:", height=400)

    if st.button("Get Results/Summary"):
        with st.spinner("Processing..."):
            if text_upload:
                summary = summarize_text(text_upload, user_query=user_query, word_limit=word_limit)
            else:
                if uploaded_file is not None:
                    temp_filename = os.path.join("temp", uploaded_file.name)
                    os.makedirs("temp", exist_ok=True)
                    with open(temp_filename, "wb") as f:
                        f.write(uploaded_file.read())

                    faiss_db = load_and_index_pdf(temp_filename)
                    results = query_indexed_pdf(faiss_db, user_query)
                    summary = summarize_text(results, user_query=user_query, word_limit=word_limit)
                else:
                    st.warning("Please upload a PDF file or paste text for summarization.")
                    summary = "" 
            st.subheader("Result/Summary:")
            st.write(summary)

elif app_mode == "Research Trends":
    st.title("Research Trends")

    time_range = st.selectbox("Select a time range:", ["Last Year", "Last 5 Years", "All Time"])
    search_query = st.text_input("Enter a search query (e.g., 'machine learning', 'cancer research'):", value="machine learning")

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