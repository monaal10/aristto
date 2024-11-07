import requests
from pyalex import Institutions, Authors
import pyalex
import logging
from classes.research_paper import ResearchPaper
from embeddings_module import rank_documents
import pandas as pd

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


def get_publisher_id_list(publisher_ranks):

    try:
        publisher_ids = {}
        df = pd.read_csv('jqr.csv')
        df_final = pd.DataFrame()
        for publisher_rank in publisher_ranks:
            df_filtered = df[df['SJR Best Quartile'] == publisher_rank]
            df_final = pd.concat([df_final, df_filtered], ignore_index=True)
        for i in range(len(df_final)):
            publisher_ids[df_final['source_id'][i]] = df_final['SJR Best Quartile'][i]
        return publisher_ids
    except Exception as e:
        raise ("Error getting SJR rank", e)


def create_http_url_for_open_alex(query, start_year, end_year, citation_count, published_in, authors):
    try:
        author_ids = get_author_id_list(authors) if authors else None
        logger.info("Fetching works from OpenAlex")
        cited_by_count = citation_count if citation_count else min_cited_by_count
        start_year_final = (str(start_year) if start_year else "1800")
        end_year_final = (str(end_year) if end_year else "2024")
        http_url = 'https://api.openalex.org/works?mailto=monaalsanghvi1998@gmail.com&search=' + query + '&filter=cited_by_count:>' + str(
            cited_by_count) + ',publication_year:>' + start_year_final + ',publication_year:<' + end_year_final

        if author_ids:
            http_url = http_url + ',author.id:' + author_ids

        http_url = http_url + "&sort=relevance_score:desc&per-page=200&page="
        return http_url
    except Exception as e:
        raise e


def get_relevant_papers(query, start_year, end_year, citation_count, published_in, authors):
    filtered_papers =[]
    paper_urls = []
    if not published_in:
        published_in = ["Q1", "Q2", "Q3", "Q4"]
    http_url = create_http_url_for_open_alex(query, start_year, end_year, citation_count, published_in,
                                             authors)
    response = requests.get(http_url)
    data = response.json()
    papers = [ResearchPaper(work) for work in data['results']]
    for paper in papers:
        try:
            publisher_ids = get_publisher_id_list(published_in)
            if paper.oa_url and paper.oa_url.endswith(".pdf") and paper.publication_id and publisher_ids.get(paper.publication_id, None):
                paper.publication_quartile = publisher_ids[paper.publication_id]
                paper_urls.append(paper.oa_url)
                filtered_papers.append(paper)
        except Exception as e:
            raise(f"Error processing paper: {e}")

    logger.info(f"Valid URLs count = {len(paper_urls)}")
    # relevant_papers = rank_documents(query, papers)
    logger.info("Fetched relevant papers")
    return papers


#get_relevant_papers("Deepfake Detection using Computer vision", 2018, 2023, None, ["Q1", "Q2"], None, None)