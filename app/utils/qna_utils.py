def format_document_references(relevant_context: str) -> str:
    """
    Formats document references for display in responses.
    
    Args:
        relevant_context: The context retrieved from the document
    
    Returns:
        Formatted references string
    """
    if not relevant_context.strip():
        return ""

    references = "\n\n📌 **Relevant Passages from Document**\n"
    for i, context in enumerate(relevant_context.split("\n\n"), 1):
        if context.strip():
            # Clean and format the context
            cleaned_context = context.strip().replace('\n', ' ')
            references += f"{i}. {cleaned_context}\n\n"
    
    return references.strip() 