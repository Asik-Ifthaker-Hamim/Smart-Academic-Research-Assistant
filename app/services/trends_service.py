import arxiv
import datetime
from collections import Counter
from app.schema.trends import ResearchTrendsResponse
from app.utils.nlp_utils import extract_keywords
from app.utils.date_utils import extract_time_period, calculate_start_date
from app.crud.trends_history import create_trends_history
from sqlalchemy.orm import Session

def analyze_research_trends(time_range: str, search_query: str, db: Session, user_id: str) -> ResearchTrendsResponse:
    """Fetches research papers from arXiv and analyzes trends over a user-specified time range."""
    try:
        value, unit = extract_time_period(time_range)
        if not value or not unit:
            value, unit = 1, 'year'
            
        start_date = calculate_start_date(value, unit)
        today = datetime.datetime.now()

        # Format dates for ArXiv query with full timestamp
        start_date_str = start_date.strftime('%Y%m%d000000')
        end_date_str = today.strftime('%Y%m%d235959')
        
        # ArXiv date-based query
        date_query = f"lastUpdatedDate:[{start_date_str} TO {end_date_str}]"
        query = f"{search_query} AND {date_query}"

        print(f"Debug - Query: {query}")

        try:
            search = arxiv.Search(
                query=query,
                max_results=100,
                sort_by=arxiv.SortCriterion.LastUpdatedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            papers = list(search.results())
            print(f"Debug - Papers found: {len(papers)}")
        except Exception as e:
            print(f"Error fetching from ArXiv: {str(e)}")
            return create_empty_response(search_query, time_range, value, unit)

        if not papers:
            return create_empty_response(search_query, time_range, value, unit)

        # Filter papers within the requested time range
        filtered_papers = [
            paper for paper in papers 
            if start_date.date() <= paper.published.date() <= today.date()
        ]

        # Standardize time-based grouping
        publication_trends = {}
        if unit == 'day':
            publication_dates = [paper.published.date() for paper in filtered_papers]
            counts = Counter(publication_dates)
            publication_trends = {date.strftime('%Y-%m-%d'): count for date, count in counts.items()}
        elif unit == 'month':
            publication_months = [paper.published.strftime('%Y-%m') for paper in filtered_papers]
            publication_trends = dict(Counter(publication_months))
        else:  # year
            publication_years = [str(paper.published.year) for paper in filtered_papers]
            publication_trends = dict(Counter(publication_years))

        # Sort publication trends by date
        publication_trends = dict(sorted(publication_trends.items()))

        # Extract and count ALL keywords without filtering
        all_keywords = [extract_keywords(f"{paper.summary} {paper.title}") for paper in filtered_papers]
        all_keywords_flat = [kw for sublist in all_keywords for kw in sublist]
        # Get all topics with their frequencies
        topic_counts = dict(Counter(all_keywords_flat))

        # Create summary statistics
        summary_stats = {
            "total_papers": len(filtered_papers),
            "time_category": f"{unit}s",
            "time_period": value,
            "date_range": f"{start_date.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}",
            "average_papers_per_period": round(len(filtered_papers) / value, 2) if value > 0 else 0
        }

        result = ResearchTrendsResponse(
            query=search_query,
            publication_trends=publication_trends,
            trending_topics=topic_counts,
            time_range=time_range,
            time_value=value,
            time_unit=unit,
            summary_stats=summary_stats
        )
        
        # Store in history
        create_trends_history(
            db=db,
            user_id=user_id,
            query=search_query,
            results={
                "publication_trends": publication_trends,
                "trending_topics": topic_counts,
                "time_range": time_range,
                "time_value": value,
                "time_unit": unit,
                "summary_stats": summary_stats
            }
        )
        
        return result

    except Exception as e:
        print(f"Error analyzing research trends: {str(e)}")
        return create_empty_response(search_query, time_range, value, unit)

def create_empty_response(search_query: str, time_range: str, value: int, unit: str) -> ResearchTrendsResponse:
    """Helper function to create empty response with proper structure"""
    today = datetime.datetime.now()
    start_date = calculate_start_date(value, unit)
    
    return ResearchTrendsResponse(
        query=search_query,
        publication_trends={},
        trending_topics={},
        time_range=time_range,
        time_value=value,
        time_unit=unit,
        summary_stats={
            "total_papers": 0,
            "time_category": f"{unit}s",
            "time_period": value,
            "date_range": f"{start_date.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}",
            "average_papers_per_period": 0
        }
    )
