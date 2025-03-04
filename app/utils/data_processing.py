from sqlalchemy.orm import Session
from app.crud.search_history import get_paper_details
from app.faiss.text_extraction import extract_text_from_link
from app.faiss.faiss_storage import store_paper_in_faiss

def extract_and_store_papers(selected_paper_ids, db: Session, faiss_index, user_id: str):
    """Extracts paper details, fetches full text from links, chunks it, and stores in FAISS."""
    # Get existing paper IDs from FAISS
    existing_paper_ids = set(getattr(faiss_index, 'paper_ids', []))
    print(f"Debug - Existing papers in FAISS: {len(existing_paper_ids)}")
    
    # Filter out papers that are already in FAISS
    new_paper_ids = [pid for pid in selected_paper_ids if str(pid) not in existing_paper_ids]
    
    if not new_paper_ids:
        print("Debug - All papers already exist in FAISS, skipping extraction and embedding")
        return
    
    print(f"Debug - Processing {len(new_paper_ids)} new papers")
    for paper_id in new_paper_ids:
        print(f"Processing new paper ID: {paper_id}")
        paper = get_paper_details(db, user_id, str(paper_id))
        if not paper:
            print(f"Could not get details for paper {paper_id}")
            continue

        # Start with basic paper information
        paper_text = f"Title: {paper.title}\nAuthors: {paper.authors}\nSummary: {paper.summary}"
        
        # Extract content from link if available
        if paper.link:
            print(f"Extracting content from link: {paper.link}")
            try:
                extracted_content = extract_text_from_link(paper.link)
                if extracted_content:
                    print(f"Successfully extracted {len(extracted_content)} characters from link")
                    paper_text += f"\nExtracted Content:\n{extracted_content}"
                else:
                    print("No content extracted from link")
            except Exception as e:
                print(f"Error extracting content from link: {str(e)}")

        # Store in FAISS with full content
        try:
            store_paper_in_faiss(faiss_index, str(paper_id), paper_text)
            print(f"Successfully stored paper {paper_id} in FAISS")
        except Exception as e:
            print(f"Error storing paper in FAISS: {str(e)}")
