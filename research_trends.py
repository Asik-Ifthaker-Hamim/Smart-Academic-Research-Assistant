import streamlit as st
import arxiv
from collections import Counter
import spacy  
import datetime  

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    st.warning("Downloading en_core_web_sm model for spacy...")
    import spacy
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def extract_keywords(text, num_keywords=5):
    """Extracts keywords from the given text using spaCy."""
    doc = nlp(text)
    keywords = [token.text for token in doc if not token.is_stop and token.is_alpha]
    keyword_counts = Counter(keywords)
    most_common_keywords = [keyword for keyword, count in keyword_counts.most_common(num_keywords)]
    return most_common_keywords

def analyze_research_trends(time_range, search_query):
    """Analyzes research trends based on time range and a search query."""
    try:
        today = datetime.date.today()
        if time_range == "Last Year":
            start_date = today.replace(year=today.year - 1)
            end_date = today
        elif time_range == "Last 5 Years":
            start_date = today.replace(year=today.year - 5)
            end_date = today
        else:
            start_date = None
            end_date = None

        if start_date and end_date:
            date_filter = f"[{start_date.strftime('%Y%m%d')} TO {end_date.strftime('%Y%m%d')}]"
            query = f"{search_query} AND submittedDate:{date_filter}" 
        else:
            query = search_query 

        search = arxiv.Search(
            query=query,
            max_results=100  
        )
        papers = list(search.results())

        if not papers:
            st.warning("No results found for the specified criteria.")
            return

        publication_years = [paper.published.year for paper in papers]

        all_keywords = []
        for paper in papers:           
            combined_text = f"{paper.summary} {paper.title}" 
            keywords = extract_keywords(combined_text)  
            all_keywords.extend(keywords)

        topic_counts = Counter(all_keywords) 

        st.subheader("Publication Trends Over Time")
        year_counts = Counter(publication_years)
        years = sorted(year_counts.keys())
        counts = [year_counts[year] for year in years]
        st.line_chart(dict(zip(years, counts)))

        st.subheader("Distribution of Research Topics")
        st.bar_chart(topic_counts)

    except Exception as e:
        st.error(f"An error occurred: {e}")