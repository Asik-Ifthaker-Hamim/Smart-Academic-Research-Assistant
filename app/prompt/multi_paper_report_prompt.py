def get_multi_paper_report_prompt(paper_details, retrieved_texts, sections, word_limit):
    papers_info = "\n\n".join(paper_details)
    
    return f"""
    Generate a comparative analysis report for the following papers:

    PRIMARY PAPERS:
    {papers_info}

    ADDITIONAL RELEVANT INFORMATION:
    {retrieved_texts}

    Please structure the report according to these sections: {', '.join(sections)}
    
    Requirements:
    1. Stay within {word_limit} words
    2. Use proper citations:
       - When discussing primary papers, cite as [Primary: Paper Title]
       - When using information from similar papers, cite as [Source: Paper Title]
    3. Compare and contrast the papers' approaches, findings, and conclusions
    4. Highlight common themes and differences
    5. Use academic language
    6. Be objective and analytical
    
    Guidelines for comparison:
    - Identify common themes across papers
    - Note significant differences in approaches or conclusions
    - Synthesize findings from all sources
    - Draw connections between related concepts
    - Highlight complementary or contradictory findings
    
    Format the report with:
    - Clear section headers
    - Proper citations throughout
    - Balanced coverage of all primary papers
    - Integration of relevant supporting information
    """