from langchain.agents import tool
from googlesearch import search
import arxiv
import re  
import time 

@tool
def google_search_with_pdf_links(query: str) -> str:
    """Searches Google and returns snippets from search results, prioritizing PDF links."""
    try:
        results = []
        for i, j in enumerate(search(query, num_results=5)):  
            try:
                time.sleep(2) 

                if j.lower().endswith(".pdf"):
                    results.append(f"{i+1}. [PDF Link]: {j}")
                else:
                    import requests
                    response = requests.get(j, timeout=5)  
                    response.raise_for_status()  
                    pdf_links = re.findall(r'href=["\'](https?://.*?\.pdf)["\']', response.text)
                    if pdf_links:
                        results.append(f"{i+1}. [PDF Link on Page]: {pdf_links[0]}")
                    else:
                        results.append(f"{i+1}. [Snippet]: {j}")  
            except requests.exceptions.RequestException as e:
                results.append(f"{i+1}. [Snippet - Error: {type(e).__name__}] {j}")  
            except Exception as e:
                results.append(f"{i+1}. [Snippet - General Error: {type(e).__name__}] {j}")
        return "\n".join(results)
    except Exception as e:
        return f"An error occurred during Google Search: {e}"

@tool
def arxiv_search(query: str) -> str:
    """Searches arXiv for academic papers and returns a summary of the top result."""
    try:
        search_results = arxiv.Search(
            query=query,
            max_results=5  
        ).results()

        papers = list(search_results)

        if not papers:
            return "No results found on arXiv."

        result_string = "" 
        for paper in papers:
            result_string += f"Title: {paper.title}\nAuthors: {', '.join(str(author) for author in paper.authors)}\nSummary: {paper.summary}\nLink: {paper.pdf_url}\n\n"
        return result_string
    except Exception as e:
        return f"An error occurred during arXiv Search: {e}"