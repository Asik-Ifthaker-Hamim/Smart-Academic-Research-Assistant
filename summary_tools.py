from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from langchain.schema import HumanMessage
from utils import get_openai_api_key
import streamlit as st

def summarize_text(text, user_query="Write a concise summary", word_limit=50):
    """Summarizes the given text using GPT-3.5-turbo, incorporating user queries and word limit."""
    try:
        model_name = "gpt-4o-mini"

        prompt_template = f"""{user_query} of the following text in no more than {word_limit} words:
        {{text}}
        
        INSTRUCTIONS: Keep the summary extremely brief and strictly adhere to the {word_limit} word limit.
        Be concise and focus only on the core result.

        SUMMARY:"""
        prompt = PromptTemplate.from_template(prompt_template)

        try:
            llm = ChatOpenAI(model_name=model_name, openai_api_key=get_openai_api_key(), temperature=0.2)
        except Exception as e:
            st.warning(f"Failed to initialize {model_name}, defaulting to gpt-3.5-turbo: {e}")
            model_name = "gpt-3.5-turbo"
            llm = ChatOpenAI(model_name=model_name, openai_api_key=get_openai_api_key(), temperature=0.2)

        llm_chain = LLMChain(llm=llm, prompt=prompt)

        stuff_chain = StuffDocumentsChain(
            llm_chain=llm_chain, document_variable_name="text"
        )

        document = Document(page_content=text)
        return stuff_chain.run([document])

    except Exception as e:
        return f"An error occurred during summarization: {e}"