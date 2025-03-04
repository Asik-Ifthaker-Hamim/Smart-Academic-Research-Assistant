import uuid
from sqlalchemy.orm import Session
from app.schema.search import PaperSearchRequest, PaperSearchResponse
from app.crud.search_history import insert_search_history
from app.utils.api_requests import arxiv_search, pubmed_search, scholarly_search

def search_papers(index_id: str, request: PaperSearchRequest, db: Session, user_id: str) -> PaperSearchResponse:
    """Searches multiple sources for research papers and stores them permanently in the database using index_id."""
    results = []
    results.extend(arxiv_search(request.query, request.num_papers, request.min_year))
    results.extend(pubmed_search(request.query))
    results.extend(scholarly_search(request.query, request.num_papers))

    response = PaperSearchResponse(query=request.query, results=results)

    for paper in results:
        paper_id = str(uuid.uuid4())  
        insert_search_history(
            db=db,
            user_id=user_id,
            paper_id=paper_id,
            index_id=index_id,
            title=paper.title,
            authors=paper.authors,
            summary=paper.summary,
            link=paper.link,
            source=paper.source
        )

    return response
