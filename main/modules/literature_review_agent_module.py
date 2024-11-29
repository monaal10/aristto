import json
from concurrent.futures import as_completed, ThreadPoolExecutor

from langchain_community.cache import InMemoryCache

from modules.embeddings_module import rank_documents
from modules.get_llm_response_module import get_model_response
from utils.constants import THEME_NUMBER_LIMIT
from utils.azure_openai_utils import get_openai_4o_mini
from utils.pdf_operations import download_pdf
from modules.relevant_papers_module import get_relevant_papers
from classes.lit_review_agent_classes import AgentState, LiteratureReview, \
    ReferenceWithMetadata, Themes, PaperValidation, InsightGeneration
from prompts.literature_review_prompts import THEME_IDENTIFICATION_PROMPT, PAPER_VALIDATION_PROMPT, \
    INFORMATION_EXTRACTION_RESPONSE_PROMPT, CREATE_LITERATURE_REVIEW_PROMPT, \
    EXTRACT_PAPER_INFO_PROMPT
from json.decoder import JSONDecodeError
from time import sleep
llm = get_openai_4o_mini()
# Cache setup
langchain_cache = InMemoryCache()


def identify_themes(query):
    try:
        llm_with_output = llm.with_structured_output(Themes)
        themes = get_model_response(llm_with_output, THEME_IDENTIFICATION_PROMPT, {"query": query})
        return themes.themes[:THEME_NUMBER_LIMIT]
    except Exception as e:
        raise f"Error in theme identification: {e}"


def validate_and_download_paper(paper, theme):
    try:
        llm_with_output = llm.with_structured_output(PaperValidation)
        downloaded_paper = paper
        response = get_model_response(llm_with_output,
                                      PAPER_VALIDATION_PROMPT,
                                      {"theme": theme,
             "paper": f""" paper_title : {paper.title} , paper_abstract : {paper.abstract}"""})
        if response.answer == True:
            downloaded_paper = download_pdf(paper)
        return downloaded_paper
    except Exception as e:
        raise (f"Error in paper validation and downloading: {e}")


def find_papers(state: AgentState):
    try:
        final_papers = []
        state.themes_with_papers = {}
        papers_to_download = 5
        for theme in state.themes:
            papers_found = 0
            papers = get_relevant_papers(theme, state.start_year, state.end_year, state.citation_count,
                                         state.published_in, state.authors)[:20]
            for i in range(0, len(papers), papers_to_download):
                if not (papers_to_download - papers_found > 0):
                    break
                for paper in papers:
                    validated_paper = validate_and_download_paper(paper, theme)
                    if validated_paper.pdf_content is not None:
                        final_papers.append(validated_paper)
                        papers_found += 1
                    if not (papers_to_download - papers_found > 0):
                        break
            state.themes_with_papers[theme] = final_papers
        return final_papers
    except Exception as e:
        raise (f"Error in paper finding: {e}")





def extract_information(papers, max_retries=3, retry_delay=1):
    """
    Extract information from papers with retry mechanism for JSONDecodeError.

    Args:
        papers: List of paper objects to process
        max_retries: Maximum number of retry attempts per paper
        retry_delay: Delay in seconds between retries
    """

    def process_single_paper(paper, attempt=1):
        try:
            json_llm = llm.bind(response_format={"type": "json_object"})
            message = get_model_response(
                json_llm,
                EXTRACT_PAPER_INFO_PROMPT,
                {"pdf_content": paper.pdf_content, "response_format": INFORMATION_EXTRACTION_RESPONSE_PROMPT}
            )

            json_message = json.loads(message.content)
            for key in json_message.keys():
                section = json_message.get(key)
                for i in range(len(section.keys())):
                    section[paper.open_alex_id + "_" + key + "_" + str(i + 1)] = section.get(str(i + 1))
                    del section[str(i + 1)]
                setattr(paper, key, json_message.get(key))
            return paper

        except JSONDecodeError as e:
            if attempt < max_retries:
                sleep(retry_delay)
                return process_single_paper(paper, attempt + 1)
            else:
                print(
                    f"Failed to decode JSON after {max_retries} attempts for paper {paper.open_alex_id}: {str(e)}")
        except Exception as e:
            raise Exception(f"Error in information extraction: {str(e)}")

    try:
        updated_papers = []
        for paper in papers:
            processed_paper = process_single_paper(paper)
            updated_papers.append(processed_paper)
        return updated_papers

    except Exception as e:
        raise Exception(f"Error processing papers: {str(e)}")


def generate_insights(papers, query):
    try:
        section_list = ["methodology", "datasets", "results", "contributions", "limitations"]
        references = {}
        papers_with_section_info = []
        for paper in papers:
            if paper:
                selected_paper_info = {'id': paper.open_alex_id, 'title': paper.title,
                                       'publication_year': paper.publication_year,
                                       'methodology': paper.methodology,
                                       'datasets': paper.datasets, 'contributions': paper.contributions,
                                       'results': paper.results, 'limitations': paper.limitations}
                papers_with_section_info.append(selected_paper_info)
                for section in section_list:
                    dic = selected_paper_info[section]
                    for key, value in dic.items():
                        references[key] = value
        response = get_model_response(llm,
                                      CREATE_LITERATURE_REVIEW_PROMPT,
                                      {"papers": json.dumps(papers_with_section_info), "query": query}
                                      )
        return format_response(response.content, references, papers)
    except Exception as e:
        raise (f"Error in insight generation: {e}")
def format_response(response, references, papers):
    try:
        reference_with_metadata_list = []
        filtered_references = {}
        for reference in references.keys():
            if reference in response:
                filtered_references[reference] = references[reference]
        for key, value in filtered_references.items():
            split_reference = key.split("_")
            paper_id = split_reference[0]
            for paper in papers:
                if paper and paper.open_alex_id == paper_id:
                    reference_with_metadata_list.append(
                        ReferenceWithMetadata(reference_id=key, paper_id=paper_id, reference_metadata=paper,
                                              reference_text=value))
        dict_response = extract_sections(response)
        summary = LiteratureReview(references=reference_with_metadata_list, insights=dict_response)
        return summary
    except Exception as e:
        raise (f"Error in formatting response: {e}")


def extract_sections(literature_review):
    try:
        dict_response = {}
        section_headers_split = literature_review.split("###")
        section_headers = [i.split("\n", 1) for i in section_headers_split[1:]]
        for i in section_headers:
            dict_response[i[0]] = i[1]
        return dict_response
    except Exception as e:
        raise (f"Error in extracting sections: {e}")


def execute_literature_review(query, start_year, end_year, citation_count, published_in, authors):
    try:
        states = []
        themes = identify_themes(query)
        papers = []
        for theme in themes:
            initial_state = AgentState(query=theme, start_year=start_year, end_year=end_year,
                                       citation_count=citation_count, published_in=published_in, authors=authors,
                                       themes=[theme])
            states.append(initial_state)
        with ThreadPoolExecutor(max_workers=8) as executor:  # Adjust number of workers based on CPU capacity
            futures = {executor.submit(find_papers, state): state for state in states}
            for future in as_completed(futures):
                paper = future.result()
                papers.extend(paper)
        unique_papers = list({paper.open_alex_id: paper for paper in papers}.values())
        ranked_papers = rank_documents(query, unique_papers)[:20]
        papers_with_info = extract_information(ranked_papers)
        answer = generate_insights(papers_with_info, query)
        return answer
    except Exception as e:
        raise (f"Error in getting literature review: {e}")
