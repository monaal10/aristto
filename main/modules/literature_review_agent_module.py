import json
from asyncio import as_completed
from concurrent.futures import ProcessPoolExecutor

from langchain_community.cache import InMemoryCache
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END, START
from utils.anthropic_utils import get_claude_haiku
from utils.pdf_operations import download_pdfs_parallel
from modules.relevant_papers_module import get_relevant_papers
from typing import Dict
from classes.lit_review_agent_classes import AgentState, PaperInformation, InsightGeneration, ThemeLiteratureReview, \
    ReferenceWithMetdadata
from prompts.literature_review_prompts import THEME_IDENTIFICATION_PROMPT, PAPER_VALIDATION_PROMPT, \
    INFORMATION_EXTRACTION_PROMPT, \
    GRAPH_BUILDING_PROMPT, INSIGHT_GENERATION_PROMPT

llm = get_claude_haiku()

# Cache setup
langchain_cache = InMemoryCache()

topic_extraction_dict = {
    "methodology": " Methodology/Processes/Algorithms used to conduct the research.",
    "contributions": "Major Findings/New Contributions of the paper.",
    "datasets": "Datasets used",
    "limitations": "Drawbacks/Limitations",
    "results": "Results of the experiments in the paper"
}

# Helper function to create Claude message
def create_claude_message(prompt: str, state: Dict, output_format):
    try:
        messages = [{
            "role": "user",
            "content": prompt.format(**state)
        }]
        llm_with_output = llm
        if output_format:
            llm_with_output = llm.with_structured_output(output_format)
            response = llm_with_output.invoke(messages)
            return response
        response = llm_with_output.invoke(messages)
        return response.content
    except Exception as e:
        raise f"Error in Claude API call: {e}"


# Node implementations with error handling
def identify_themes(query):
    try:
        themes_text = create_claude_message(THEME_IDENTIFICATION_PROMPT, {"query": query}, None)
        themes = [theme.strip() for theme in themes_text.split(',')]
        themes.append(query)
        return themes
    except Exception as e:
        raise f"Error in theme identification: {e}"



def find_papers(state: AgentState) -> AgentState:
    try:
        state.themes_with_papers = {}
        papers_to_download = 5
        for theme in state.themes:
            final_papers = []
            papers_found = 0
            # Update the function call with actual values
            papers = get_relevant_papers(theme, state.start_year, state.end_year, state.citation_count,
                                         state.published_in, state.authors)
            for i in range(0, len(papers), papers_to_download):
                if not (papers_to_download - papers_found > 0):
                    break
                downloaded_papers = download_pdfs_parallel(paper for paper in papers[i:i + papers_to_download])
                for paper in downloaded_papers[i:i + papers_to_download]:
                        if paper.pdf_content:
                            response = create_claude_message(
                                PAPER_VALIDATION_PROMPT,
                                {"theme": theme,
                                 "paper": f""" paper_title : {paper.title} , paper_abstract : {paper.abstract}"""}, None
                            )
                            if response.lower() == "true":
                                final_papers.append(paper)
                                papers_found += 1
                        if not (papers_to_download - papers_found > 0):
                            break
            state.themes_with_papers[theme] = final_papers
        return state
    except Exception as e:
        raise (f"Error in paper finding: {e}")


def extract_information(state: AgentState) -> AgentState:
    try:
        for theme, papers in state.themes_with_papers.items():
            updated_papers = []
            for paper in papers:
                for key, value in topic_extraction_dict.items():
                    message = create_claude_message(
                        INFORMATION_EXTRACTION_PROMPT,
                        {"pdf_content": paper.pdf_content, "query": state.query, "information_to_extract": value},
                        PaperInformation
                    )
                    setattr(paper, key, message)
                updated_papers.append(paper)
            state.themes_with_papers[theme] = updated_papers
        return state
    except Exception as e:
        raise f"Error in information extraction: {e}"


def generate_insights(state: AgentState) -> AgentState:
    try:
        final_summaries = []
        for theme, papers in state.themes_with_papers.items():
            papers_with_section_info = []
            for paper in papers:
                selected_paper_info = {'id': paper.open_alex_id, 'title': paper.title,
                                       'abstract': paper.abstract, 'publication_year': paper.publication_year,
                                       'methodology': paper.methodology,
                                       'datasets': paper.datasets, 'contributions': paper.contributions,
                                       'results': paper.results, 'limitations': paper.limitations}
                papers_with_section_info.append(selected_paper_info)

            response = create_claude_message(
                INSIGHT_GENERATION_PROMPT,
                {"papers": json.dumps(papers_with_section_info), "query": state.query}, InsightGeneration
            )
            reference_with_metadata_list = []
            references = response.get("references")
            for reference in references.values():
                paper_object = None
                paper_id = reference.get("paper_id")
                for paper in papers:
                    if paper.oa_url == paper_id:
                        reference_with_metadata_list.append(
                            ReferenceWithMetdadata(reference=reference, reference_metadata=paper_object))
            summary = ThemeLiteratureReview(theme=theme, papers=reference_with_metadata_list, insights=response)
            final_summaries.append(summary)
        state.literature_review = final_summaries
        """final_summaries = []
        for graph in state.graph_data:
            message = create_claude_message(
                INSIGHT_GENERATION_PROMPT,
                {"graph": graph, "query": state.query}, None
            )
            final_summaries.append(message)
        state.insights = final_summaries
        state.memory["insights_generated"] = len(state.insights)"""
    except Exception as e:
        state.literature_review = []
        raise(f"Error in insight generation: {e}")
    return state


def process_theme(state):
    find_papers_state = find_papers(state)
    extract_information_state = extract_information(find_papers_state)
    generate_insights_state = generate_insights(extract_information_state)
    return generate_insights_state
# Usage example
def analyze_research_query(query, start_year, end_year, citation_count, published_in, authors):
    try:
        literature_review = []
        states = []
        themes = identify_themes(query)
        for theme in themes:
            initial_state = AgentState(query=query, start_year=start_year, end_year=end_year,
                                       citation_count=citation_count, published_in=published_in, authors=authors,
                                       theme=theme)
            states.append(initial_state)
        with ProcessPoolExecutor(max_workers=len(themes)) as executor:  # Adjust number of workers based on CPU capacity
            futures = {executor.submit(process_theme, state): state for state in states}
            for future in as_completed(futures):
                theme_result = future.result()
                literature_review.append(theme_result.literature_review)
        return literature_review
    except Exception as e:
        print(f"Error in research analysis: {e}")
        return None
# Example usage
"""if __name__ == "__main__":
    query = ("What are the recent methods to detect deepfake and how have they evolved over the years?")
    result = analyze_research_query(query, 2000, 2024, 5, ["Q1", "Q2"], None)

def build_graph(state: AgentState) -> AgentState:
    try:
        graphs = []
        for theme, papers in state.themes_with_papers.items():
            papers_for_graph = []
            for paper in papers:
                selected_paper_info = {'id': paper.open_alex_id, 'title': paper.title,
                                       'extracted_content': paper.extracted_info, 'abstract': paper.abstract}
                papers_for_graph.append(selected_paper_info)

            message = create_claude_message(
                GRAPH_BUILDING_PROMPT,
                {"papers": papers_for_graph, "query": state.query}, None
            )
            graphs.append({"paper_info": papers_for_graph, "graph": message})
        state.graph_data = graphs
        state.memory["graph_built"] = True
    except Exception as e:
        print(f"Error in graph building: {e}")
        state.graph_data = {}
    return state"""
