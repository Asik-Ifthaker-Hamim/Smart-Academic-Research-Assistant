from langchain.agents import tool
import arxiv
import re
import time

from scholarly import scholarly  
from Bio import Entrez  


@tool
def scholarly_search(query: str) -> str:
    """Searches Google Scholar returns snippets"""
    try:
        scholar_string = ""
        search_query = scholarly.search_pubs(query)  
        i = 0
        while i < 5:  
            results_scholar = next(search_query, None) 
            if results_scholar is not None: 
                scholar_string += f"Title: {results_scholar['bib']['title']}\n"  
                scholar_string += f"Authors: {results_scholar['bib']['author']}\n"  
                scholar_string += f"Link: {results_scholar['pub_url']}\n\n" 
            else:
                return "No results found on Scholarly."
            i += 1
        return scholar_string
    except Exception as e:  
        return f"An error occurred during Scholarly Search: {e}"


@tool
def pubmed_search(query: str) -> str:
    """Searches Pubmed API"""
    try:
        Entrez.email = "Your.Name.Here@example.org" 
        handle = Entrez.esearch(db="pubmed", term=query, retmax="5")  
        record = Entrez.read(handle) 
        id_list = record["IdList"]  
        pub_string = ""
        if id_list:  
            for pubmed_id in id_list: 
                handle = Entrez.esummary(db="pubmed", id=pubmed_id, retmode="text")  
                record = Entrez.read(handle)  

                pub_string += f"Title: {record[0]['Title']}\n"  
                pub_string += f"Authors: {record[0]['AuthorList']}\n"  
                pub_string += f"Link: https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/\n\n"  
            return pub_string
        else:
            return "No results found on PubMed."  
    except Exception as e:  
        return f"An error occurred during PubMed Search: {e}" 


@tool
def arxiv_search(query: str) -> str:  
    """Searches arXiv for academic papers and returns a summary of the top result."""
    try:
        search_results = arxiv.Search(query=query, max_results=5).results() 
        papers = list(search_results)  
        if not papers:  
            return "No results found on arXiv."  
        result_string = ""  
        for paper in papers:  
            result_string += f"Title: {paper.title}\nAuthors: {', '.join(str(author) for author in paper.authors)}\nSummary: {paper.summary}\nLink: {paper.pdf_url}\n\n"  
        return result_string  
    except:
        return f"There is an issue for the result."