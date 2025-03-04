def get_single_paper_report_prompt(paper_details, retrieved_texts, sections, word_limit):
    return f"""
    Generate a structured analysis report for the following paper:

    {paper_details[0]}

    Additional relevant information from similar papers:
    {retrieved_texts}

    Please structure the report according to these sections: {', '.join(sections)}
    
    Requirements:
    1. Stay within {word_limit} words
    2. When using information from similar papers, cite the source using [Source: Paper Title]
    3. Focus on key insights and findings
    4. Use academic language
    5. Be objective and analytical
    
    Format the report with clear section headers and proper citations.
    """
