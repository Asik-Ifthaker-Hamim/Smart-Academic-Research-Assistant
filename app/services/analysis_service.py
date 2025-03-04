from sqlalchemy.orm import Session
from app.crud.search_history import get_paper_details
from app.prompt.single_paper_report_prompt import get_single_paper_report_prompt
from app.prompt.multi_paper_report_prompt import get_multi_paper_report_prompt
from app.faiss.faiss_index import load_or_create_faiss
from app.faiss.faiss_search import search_faiss
from app.utils.data_processing import extract_and_store_papers, extract_text_from_link
from app.core.dependencies import get_openai_client, get_embedding_model

faiss_index = load_or_create_faiss()
embedding_model = get_embedding_model()

def generate_analysis_report(user_id: str, selected_paper_ids: list, sections: list, db: Session, word_limit: int = 1000): 
    """Generates a structured analysis report using FAISS-based RAG."""
    try:
        print(f"Debug - Input parameters:")
        print(f"user_id: {user_id}")
        print(f"selected_paper_ids: {selected_paper_ids}")
        print(f"sections: {sections}")
        print(f"word_limit: {word_limit}")

        # Convert all paper IDs to strings for consistent comparison
        selected_paper_str_ids = [str(pid) for pid in selected_paper_ids]
        
        # Check which papers are already in FAISS
        existing_papers = set(faiss_index.paper_ids)
        new_papers = [pid for pid in selected_paper_str_ids if pid not in existing_papers]
        
        print(f"Debug - Papers already in FAISS: {len(existing_papers)}")
        print(f"Debug - New papers to process: {len(new_papers)}")

        is_single_paper = len(selected_paper_ids) == 1
        llm = get_openai_client()

        # Only process new papers
        if new_papers:
            print("Extracting and storing new papers with full content...")
            extract_and_store_papers(new_papers, db, faiss_index, user_id)
        else:
            print("All papers already exist in FAISS, skipping extraction")

        # Get paper details including any extracted content
        paper_details, papers_text = [], []
        paper_sources = {}  # Store paper sources for references
        
        for paper_id in selected_paper_ids:
            paper_str_id = str(paper_id)
            print(f"Debug - Fetching main paper details for: {paper_str_id}")
            paper = get_paper_details(db, user_id, paper_str_id)

            if not paper:
                continue

            print(f"Debug - Found main paper: {paper.title}")
            
            # Store paper source information
            paper_sources[paper_str_id] = {
                'title': paper.title,
                'authors': paper.authors,
                'link': paper.link if paper.link else "No link available"
            }
            
            # Include link information in paper details
            paper_info = [
                f"Title: {paper.title}",
                f"Authors: {paper.authors}",
                f"Summary: {paper.summary}"
            ]
            if paper.link:
                paper_info.append(f"Source: {paper.link}")
                try:
                    extracted_content = extract_text_from_link(paper.link)
                    if extracted_content and not extracted_content.startswith("Error"):
                        preview = extracted_content[:500] + "..." if len(extracted_content) > 500 else extracted_content
                        paper_info.append(f"Extracted Content Preview: {preview}")
                except Exception as e:
                    print(f"Error extracting content for main paper: {str(e)}")
            
            paper_details.append("\n".join(paper_info))
            papers_text.append(f"{paper.title} {paper.summary}")

        if not paper_details:
            return {"report": "Error: No valid papers found for analysis."}

        # Search for similar content using full text
        query = ' '.join(papers_text)
        query_embedding = embedding_model.embed_query(query[:8000])

        retrieved_indices = search_faiss(faiss_index, query_embedding)
        print(f"📌 Debug: FAISS retrieved indices: {retrieved_indices}")

        # Get similar papers with their full content and track sources
        retrieved_texts = []
        seen_content = set()
        for idx in retrieved_indices:
            if 0 <= idx < len(faiss_index.paper_ids):
                retrieved_paper_id = str(faiss_index.paper_ids[idx])
                print(f"Debug - Attempting to fetch similar paper: {retrieved_paper_id}")
                paper = get_paper_details(db, user_id, retrieved_paper_id)

                if paper:
                    # Store source information for this paper
                    if retrieved_paper_id not in paper_sources:
                        paper_sources[retrieved_paper_id] = {
                            'title': paper.title,
                            'authors': paper.authors,
                            'link': paper.link if paper.link else "No link available"
                        }

                    # Include extracted content if available
                    content = [
                        f"[Source: {paper.title}]",  # Add source marker
                        f"Summary: {paper.summary}"
                    ]
                    if paper.link:
                        try:
                            extracted = extract_text_from_link(paper.link)
                            if extracted:
                                content.append("Extracted content:")
                                content.append(extracted[:1000])
                        except Exception as e:
                            print(f"Error extracting content from similar paper: {str(e)}")
                    
                    full_content = "\n".join(content)
                    if full_content not in seen_content:
                        seen_content.add(full_content)
                        retrieved_texts.append(full_content)
                        print(f"Debug - Added similar paper with content: {paper.title}")

        # Generate report with sources
        return generate_report_with_references(
            paper_details, 
            retrieved_texts, 
            sections, 
            word_limit, 
            is_single_paper, 
            llm,
            paper_sources
        )

    except Exception as e:
        print(f"Debug - Error: {str(e)}")
        return {"report": f"Error generating report: {str(e)}"}

def generate_report_with_references(paper_details, retrieved_texts, sections, word_limit, is_single_paper, llm, paper_sources):
    """Generate report with references section."""
    # Generate main report
    prompt = get_single_paper_report_prompt(paper_details, retrieved_texts, sections, word_limit) if is_single_paper else get_multi_paper_report_prompt(paper_details, retrieved_texts, sections, word_limit)
    
    response = llm.invoke(prompt)
    main_report = response.content if hasattr(response, "content") else str(response)

    # Generate references section
    references = "\n\nReferences:\n"
    for paper_id, source in paper_sources.items():
        references += f"- {source['title']} by {source['authors']}\n  Link: {source['link']}\n"

    # Combine main report with references
    full_report = f"{main_report}\n{references}"
    
    return {"report": full_report}

