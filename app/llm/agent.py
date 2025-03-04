from typing import Dict, List
from langchain.agents import initialize_agent, Tool, AgentType
from app.llm.chat_llm import create_chat_llm
from app.prompt.agent_prompts import RESEARCH_AGENT_PREFIX
from app.llm.agent_tools import ReferenceTracker, EnhancedSerperTool, firecrawl_scraper


def create_research_agent():
    """Initializes the research chat assistant."""
    ref_tracker = ReferenceTracker()
    search_tool = EnhancedSerperTool(ref_tracker)

    llm = create_chat_llm()

    tools = [
        Tool(
            name="Web_Search",
            func=search_tool.run,
            description="Search the web for research topics. Returns up to 3 relevant sources."
        ),
        Tool(
            name="Page_Scraper",
            func=lambda u: firecrawl_scraper(u, ref_tracker),
            description="Scrape content from specific URLs. Input must be a valid URL."
        )
    ]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,  
        verbose=False,  
        max_iterations=5,
        handle_parsing_errors=True,
        agent_kwargs={
            "prefix": RESEARCH_AGENT_PREFIX
        }
    )
    
    return agent, ref_tracker 