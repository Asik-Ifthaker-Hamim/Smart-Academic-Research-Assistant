import arxiv
import uuid
from scholarly import scholarly
from Bio import Entrez
from app.schema.search import PaperMetadata
from app.core.config import settings


Entrez.email = settings.ENTREZ_EMAIL

def arxiv_search(query: str, num_papers: int, min_year: int) -> list:
    """Searches ArXiv for research papers."""
    papers = []
    try:
        search = arxiv.Search(query=query, max_results=num_papers)
        for result in arxiv.Client().results(search):
            if result.updated.year >= min_year:
                papers.append(PaperMetadata(
                    paper_id=str(uuid.uuid4()),  
                    source="ArXiv",
                    title=result.title,
                    authors=', '.join(author.name for author in result.authors),
                    summary=result.summary,
                    link=result.pdf_url or result.entry_id
                ))
        return papers
    except Exception as e:
        print(f"Error fetching from ArXiv: {str(e)}")
        return []

def pubmed_search(query: str) -> list:
    """Fetches research papers from PubMed."""
    papers = []
    try:
        handle = Entrez.esearch(db="pubmed", term=query, retmax=5)
        record = Entrez.read(handle)
        for pubmed_id in record.get("IdList", []):
            summary_handle = Entrez.esummary(db="pubmed", id=pubmed_id)
            summary_record = Entrez.read(summary_handle)
            papers.append(PaperMetadata(
                paper_id=str(uuid.uuid4()),  
                source="PubMed",
                title=summary_record[0].get('Title', 'No Title'),
                authors=', '.join(summary_record[0].get('AuthorList', ['No Authors'])),
                summary=summary_record[0].get('Summary', 'N/A'),
                link=f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/"
            ))
        return papers
    except Exception as e:
        print(f"Error fetching from PubMed: {str(e)}")
        return []

def scholarly_search(query: str, num_papers: int) -> list:
    """Searches Google Scholar and extracts relevant details properly."""
    papers = []
    try:
        search_query = scholarly.search_pubs(query)
        for _ in range(num_papers):
            try:
                result = next(search_query)

                papers.append(PaperMetadata(
                    paper_id=str(uuid.uuid4()),  
                    source="Google Scholar",
                    title=result['bib'].get('title', 'No Title'),
                    authors=', '.join(result['bib'].get('author', ['No Authors'])),
                    summary=result['bib'].get('abstract', 'N/A'),
                    link=result.get('pub_url', result.get('eprint_url', 'No Link'))
                ))

            except StopIteration:
                break
        return papers
    except Exception as e:
        print(f"Error fetching from Google Scholar: {str(e)}")
        return []