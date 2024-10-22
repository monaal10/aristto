import requests
from pyalex import Works, Institutions, Authors, Publishers
import pyalex
import logging
import re
from research_paper import ResearchPaper
#from embedding_model import get_embedding, calculate_similarity_scores
from get_openai_embeddings import rank_documents
import json
from download_pdf import generate_chunks
from concurrent.futures import ThreadPoolExecutor, as_completed
import time # remove before production
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
    paper_urls = []
    
    http_url = create_http_url_for_open_alex(query, start_year, end_year, citation_count, published_in, published_by_institutions, authors)
    response = requests.get(http_url)
    data = response.json()

    # Parallelize the creation of ResearchPaper objects
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(ResearchPaper, work) for work in data['results']]
        
        for future in as_completed(futures):
            try:
                paper_obj = future.result()
                if paper_obj.oa_url and paper_obj.oa_url.endswith(".pdf"):
                    paper_urls.append(paper_obj.oa_url)
                papers.append(paper_obj)
            except Exception as e:
                logger.error(f"Error processing paper: {e}")

    logger.info(f"Valid URLs count = {len(paper_urls)}")

    # Parallelize ranking documents
    def rank_document_parallel(query, papers_batch):
        return rank_documents(query, papers_batch)
    
    relevant_papers = []
    max_workers = 5
    with ThreadPoolExecutor(max_workers=max_workers) as rank_executor:
        rank_futures = [
            rank_executor.submit(rank_document_parallel, query, papers[i:i+max_workers])
            for i in range(0, len(papers), max_workers)
        ]
        
        for future in as_completed(rank_futures):
            try:
                ranking_result = future.result()
                relevant_papers.extend(ranking_result)
            except Exception as e:
                logger.error(f"Error when trying to rank documents: {e}")

    # Parallelize chunk generation
    def generate_chunk_parallel(urls_batch, query):
        return generate_chunks(urls_batch, query)
    
    start_time = time.time()
    chunks = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as chunk_executor:
        chunk_futures = [
            chunk_executor.submit(generate_chunk_parallel, paper_urls[i:i+10], query)
            for i in range(0, len(paper_urls), 10)  # Process in batches of 10 URLs
        ]
        
        for future in as_completed(chunk_futures):
            try:
                chunk_result = future.result()
                chunks.extend(chunk_result)  # Append chunk results correctly
            except Exception as e:
                logger.error(f"Error generating chunks: {e}")

    logger.info("Fetched relevant papers")
    logger.info("Parallel process ended here")
    logger.info(f"Total Execution time for PDF download and chunk creation - {time.time() - start_time}")
    
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
