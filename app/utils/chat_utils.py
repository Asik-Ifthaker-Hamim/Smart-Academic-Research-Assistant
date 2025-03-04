def format_references(ref_tracker) -> str:
    """Formats references for display in responses."""
    if not ref_tracker.sources:
        return ""
    
    references = "\n\n📌 **References**\n" + "\n".join(
        f"{s['id']}. [{s['title']}]({s['url']})"
        for s in ref_tracker.sources
    )
    return references
