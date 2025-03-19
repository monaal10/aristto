import json
from concurrent.futures import as_completed, ThreadPoolExecutor
import re

from main.modules.open_alex_index_module import get_relevant_papers_from_open_alex, get_referenced_papers
from main.classes.answer_a_question_classes import AnswerReference, AskQuestionOutput, Answer
from main.modules.get_llm_response_module import get_model_response
from main.utils.constants import SEARCH_QUERY_NUMBER_LIMIT
from main.utils.llm_utils import get_openai_4o_mini, get_claude, get_o3_mini_medium, get_o3_mini, get_o3_mini_high
from main.utils.pdf_operations import download_pdf
from main.classes.lit_review_agent_classes import SearchQueriesAndTitle
from main.prompts.literature_review_prompts import THEME_IDENTIFICATION_PROMPT, GENERATE_DEEP_RESEARCH_REPORT_PROMPT, VALIDATE_AND_EXTRACT_RELEVANT_CONTEXT_PROMPT
import logging
from main.utils.mocks import PROCESSED_RESULTS
from main.modules.answer_a_question_module import generate_searchable_query

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

llm = get_openai_4o_mini()
#gemini = get_gemini_flash_2()
o3_low = get_o3_mini()
o3 = get_o3_mini_high()
claude = get_claude()


def generate_search_queries(query, previous_search_queries, conversation_history, queries_to_generate, retry_number=1):
    try:
        llm_with_output = o3_low.with_structured_output(SearchQueriesAndTitle)
        search_queries_with_title = get_model_response(llm_with_output, THEME_IDENTIFICATION_PROMPT, {"query": query,
                                                                                   "previous_search_queries":
                                                                                       previous_search_queries,
                                                                                           "conversation_history": conversation_history,
                                                                                                      "queries_to_generate": queries_to_generate})
        return search_queries_with_title
    except Exception as e:
        if isinstance(e, AttributeError):
            if retry_number < 3:
                generate_search_queries(query, previous_search_queries, conversation_history, queries_to_generate, retry_number + 1)
        raise Exception(f"Error in theme identification: {e}")


def validate_and_extract_context(papers, query, theme):
    """
    Combined function that validates papers and extracts relevant context in one step.
    Only processes papers published before 2024 with citation count > 10.
    Makes a single LLM call that both validates and extracts context.
    """
    try:
        # Filter papers based on year and citation count
        filtered_papers = []
        for paper in papers:
            if (hasattr(paper, 'publication_year') and paper.publication_year < 2024 and
                    hasattr(paper, 'cited_by_count') and paper.cited_by_count > 10):
                filtered_papers.append(paper)

        if not filtered_papers:
            return []

        final_results = []

        # Process each paper
        for paper in filtered_papers:
            downloaded_paper = download_pdf(paper)

            if downloaded_paper is not None:
                # Set PDF content if missing
                if downloaded_paper.pdf_content is None:
                    if downloaded_paper.abstract:
                        downloaded_paper.pdf_content = downloaded_paper.abstract
                    else:
                        continue
                try:
                    # Make a single LLM call for both validation and extraction
                    context_response = get_model_response(
                        o3_low,
                        VALIDATE_AND_EXTRACT_RELEVANT_CONTEXT_PROMPT,
                        {
                            "user_query": query,
                            "paper_text": downloaded_paper.pdf_content,
                            "search_query": theme
                        }
                    )

                    if context_response and context_response.content:
                        context = context_response.content
                        # Skip if the response indicates the paper is not relevant
                        if context.strip() != "NOT_RELEVANT" and len(context.strip()) > 0:
                            final_results.append({
                                "paper_id": downloaded_paper.open_alex_id,
                                "context": context,
                                "paper": downloaded_paper
                            })
                except Exception as e:
                    logger.error(f"Error processing paper {downloaded_paper.open_alex_id}: {e}")

        return final_results
    except Exception as e:
        raise Exception(f"Error in paper validation and context extraction: {e}")


def find_papers(query, theme, start_year, end_year, citation_count, published_in, authors, sjr):
    try:
        batch = 5
        final_results = []

        # Get Lit reviews
        lit_review_reference_documents, lit_review_relevant_documents = get_relevant_papers_from_open_alex(
            theme, start_year, end_year, citation_count, authors, published_in, sjr, [], True)

        # Get normal papers
        normal_reference_documents, relevant_documents = get_relevant_papers_from_open_alex(
            query, start_year, end_year, citation_count, authors, published_in, sjr, [], False)

        # Merge results
        reference_documents = lit_review_reference_documents[:8] + normal_reference_documents[:10]

        for document in reference_documents:
            paper = document["paper_metadata"]
            referenced_paper_docs = get_referenced_papers(paper.referenced_works_ids, theme)
            referenced_papers = [doc["paper_metadata"] for doc in referenced_paper_docs]
            papers = [paper] + referenced_papers

            for i in range(0, len(papers), batch):
                batch_results = validate_and_extract_context(papers[i:i + batch], query, theme)
                final_results.extend(batch_results)

        return final_results
    except Exception as e:
        raise Exception(f"Error in paper finding and processing: {e}")

def get_relevant_context(query, themes, start_year, end_year, citation_count, published_in, authors, jqr):
    try:
        all_results = []
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(
                    find_papers, query, theme, start_year, end_year, citation_count, published_in, authors, jqr
                ): theme for theme in themes
            }

            for future in as_completed(futures):
                results = future.result()
                all_results.extend(results)

            # Remove duplicates by paper_id
        unique_results = {}
        for result in all_results:
            if result["paper_id"] not in unique_results:
                unique_results[result["paper_id"]] = result

        processed_results = list(unique_results.values())
        return processed_results
    except Exception as e:
        raise Exception(f"Error in paper finding and processing: {e}")


def generate_final_report(query, all_contexts, model):
    """
    Generate the final comprehensive report using all gathered contexts.
    """
    try:
        # Extract just the context data for the report generation
        context_only = [{"paper_id": item["paper_id"], "context": item["context"]} for item in all_contexts]

        response = get_model_response(model, GENERATE_DEEP_RESEARCH_REPORT_PROMPT,
                                      {"papers": json.dumps(context_only), "query": query})
        return response.content
    except Exception as e:
        raise Exception(f"Error in final report generation: {str(e)}")


def format_response(response, references):
    try:
        final_references = []
        reference_ids = re.findall(r'\[(.*?)\]', response)
        used_ids = set()
        for reference_id in reference_ids:
            for reference in references:
                if reference_id == reference.get("paper_id") and reference_id not in used_ids:
                    final_references.append(
                        AnswerReference(
                            reference_text=reference.get("context"),
                            reference_id=reference_id,
                            paper=reference.get("paper")
                        )
                    )
                    used_ids.add(reference_id)
        relevant_papers = []
        for reference in references:
            if reference.get("paper_id") not in used_ids:
                relevant_papers.append(reference.get("paper"))
        return AskQuestionOutput(references=final_references, answer=response, relevant_papers=relevant_papers)
    except Exception as e:
        raise Exception(f"Error in formatting response: {e}")



def invoke_deep_research_agent(query, start_year, end_year, citation_count, published_in, authors, jqr,
                               conversation_history):
    try:
        search_queries_with_title = generate_search_queries(query, [], conversation_history, 5)
        search_queries = search_queries_with_title.search_queries
        title = search_queries_with_title.title
        processed_results = get_relevant_context(query, search_queries, start_year, end_year, citation_count, published_in,
                                                 authors, jqr)
        if len(processed_results) < 100:
            if len(processed_results) <= 50:
                new_queries_to_generate = 5
            elif 50 < len(processed_results) < 75:
                new_queries_to_generate = 3
            else:
                new_queries_to_generate = 2
            response = generate_search_queries(query, [search_queries], conversation_history,
                                               new_queries_to_generate)
            new_search_queries = response.search_queries
            new_processed_results = get_relevant_context(query, new_search_queries, start_year, end_year, citation_count,
                                                     published_in,
                                                     authors, jqr)
            processed_results.extend(new_processed_results)
        if len(processed_results) == 0:
            no_papers_found_answer = "No relevent papers found, please update your search query/filters"
            conversation_history.append(("human", query))
            conversation_history.append(("assistant", no_papers_found_answer))
            return AskQuestionOutput(
                references=[], answer=no_papers_found_answer, relevant_papers=[]), conversation_history, title
        context_for_llm = [{"paper_id": result["paper_id"], "context": result["context"]} for
                           result in processed_results]
        # Generate the final report using all contexts
        answer = generate_final_report(query, context_for_llm, o3)

        # Format the response
        formatted_answer = format_response(answer, processed_results)

        # Update conversation history
        conversation_history.append(("human", query))
        conversation_history.append(("assistant", answer))

        return formatted_answer, conversation_history, title
    except Exception as e:
        raise Exception(f"Error in getting literature review: {e}")




"""query = ("Give me a comprehensive lit review on the topic undulatory ﬁn motions in ﬁsh-like robots. Give me field "
         "progression, methodologies and comparisons, some research gaps and any other section you feel is important to "
         "know for a researcher.")
answer = invoke_deep_research_agent(query, None, None, None, [], [], [], [])
print()
#ans = generate_final_report(query, PROCESSED_RESULTS, o3)
ans = generate_final_report(query, PROCESSED_RESULTS, o3)
fin = format_response(ans, PROCESSED_RESULTS)
print()
"""