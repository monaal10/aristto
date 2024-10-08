import requests
from pyalex import Works, Institutions, Authors, Publishers
import pyalex
import logging
import re
from research_paper import ResearchPaper
#from embedding_model import get_embedding, calculate_similarity_scores
from get_openai_embeddings import rank_documents
import json
# Configure logging
logger = logging.getLogger(__name__)
pyalex.config.email = "monaalsanghvi1998@gmail.com"
min_cited_by_count = 20


def create_strings_for_filters(filter_list):
    filter_string = ""
    for filter in filter_list:
        filter_string += str(filter) + "|"
    return filter_string[:len(filter_string) - 1]


def get_author_id_list(authors):
    author_ids = ""
    author_list = []
    if authors:
        author_list = Authors().search(create_strings_for_filters(authors)).get()
    for author in author_list:
        id = author['id'].split(".org/")
        author_ids += id[1] + "|"
    return author_ids[:len(author_ids) - 1]


def get_institution_id_list(institutions):
    institution_list = []
    institution_ids = ""
    if institutions:
        institution_list = Institutions().search(create_strings_for_filters(institutions)).get()
    for institution in institution_list:
        id = institution['id'].split(".org/")
        institution_ids += id[1] + "|"
    return institution_ids[:len(institution_ids) - 1]


def get_publisher_id_list(publishers):
    publisher_list = []
    publisher_ids = ""
    if publishers:
        publisher_list = Publishers().search(create_strings_for_filters(publishers)).get()
    for publisher in publisher_list:
        id = publisher['id'].split(".org/")
        publisher_ids += id[1] + "|"
    return publisher_ids[:len(publisher_ids) - 1]

def extract_doi(doi_url):
    parts = re.split(r'/+', doi_url)
    
    if "doi.org" in parts:
        index = parts.index("doi.org")
        doi = "/".join(parts[index + 1:]) 
        return doi
    return None
def create_http_url_for_open_alex(query, start_year, end_year, citation_count, published_in, published_by_institutions,
                                  authors):
    try:

        institution_ids = get_institution_id_list(published_by_institutions)
        #author_ids = get_author_id_list(authors)
        publisher_ids = get_publisher_id_list(published_in)
        logger.info("Fetching works from OpenAlex")
        cited_by_count = citation_count if citation_count else min_cited_by_count
        start_year_final = (str(start_year) if start_year else "1800")
        end_year_final = (str(end_year) if end_year else "2024")
        http_url = 'https://api.openalex.org/works?mailto=monaalsanghvi1998@gmail.com&search=' + query + '&filter=cited_by_count:>' + str(
            cited_by_count) + ',publication_year:>' + start_year_final + ',publication_year:<' + end_year_final

        # if len(author_ids) > 0:
        #    http_url = http_url + ',authors.id:' + author_ids

        if len(publisher_ids) > 0:
            http_url = http_url + ',best_oa_location.source.host_organization:' + publisher_ids

        if len(institution_ids) > 0:
            http_url = http_url + ',institutions.id:' + institution_ids
        http_url = http_url + "&sort=relevance_score:desc&per-page=50&page=1"
        return http_url
    except Exception as e:
        raise e


def get_relevant_papers(query, start_year, end_year, citation_count, published_in, published_by_institutions, authors):
    papers = []
    http_url = create_http_url_for_open_alex(query, start_year, end_year, citation_count, published_in,
                                             published_by_institutions, authors)
    response = requests.get(http_url)
    data = response.json()
    for work in data['results']:
        # doi = work.get("doi") - call the get_summary_reference method to get the paper details using doi
        papers.append(ResearchPaper(work))
    relevant_papers = rank_documents(query, papers)
    logger.info("fetched relevant papers")
    return relevant_papers
def get_summary_reference(doi):
    # Getting Reference and summary from semantic Scholar
    try:
        url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,references,abstract"
        response = requests.get(url).json()
        return {
            "title":response.get("title"),
            "summary": response.get("abstract","No Summary Available"),
            "references":response.get("references",[])
        }
    except Exception as e:
        logger.error(f"Error fetching data from Semantic Scholar: {str(e)}")
        return None
