import requests
from pyalex import Institutions, Authors
import pyalex
import logging
from main.classes.research_paper import ResearchPaper
# from embeddings_module import rank_documents
import pandas as pd

from main.utils.convert_data import convert_oa_response_to_research_paper
from main.modules.embeddings_module import rank_documents

# Configure logging
logger = logging.getLogger(__name__)
pyalex.config.email = "monaalsanghvi1998@gmail.com"
min_cited_by_count = 0


def create_strings_for_filters(filter_list):
    filter_string = ""
    for filter in filter_list:
        filter_string += str(filter) + "|"
    return filter_string[:len(filter_string) - 1]


def get_author_id_list(authors):
    try:
        author_ids = ""
        author_list = []
        if authors:
            author_list = Authors().search(create_strings_for_filters(authors)).get()
        for author in author_list:
            id = author['id'].split(".org/")
            author_ids += id[1] + "|"
        return author_ids[:len(author_ids) - 1]
    except Exception as e:
        raise f" Could not get author ids from openAlex : {e}"


def get_institution_id_list(institutions):
    institution_list = []
    institution_ids = ""
    if institutions:
        institution_list = Institutions().search(create_strings_for_filters(institutions)).get()
    for institution in institution_list:
        id = institution['id'].split(".org/")
        institution_ids += id[1] + "|"
    return institution_ids[:len(institution_ids) - 1]


def get_publisher_id_list(publisher_ranks, dataset_id):

    try:
        publisher_ids = {}
        df = pd.read_csv('modules/jqr.csv')
        df_final = pd.DataFrame()
        for publisher_rank in publisher_ranks:
            df_filtered = df[df['sjr'] == publisher_rank]
            df_final = pd.concat([df_final, df_filtered], ignore_index=True)
        for i in range(len(df_final)):
            publisher_ids[df_final[dataset_id][i]] = df_final['sjr'][i]
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
        raise f"Could not form http url from given parameters: {e}"


def get_relevant_papers(query, start_year, end_year, citation_count, published_in, authors):
    http_url = create_http_url_for_open_alex(query, start_year, end_year, citation_count, published_in,
                                             authors)
    response = requests.get(http_url)
    data = response.json()
    papers = [convert_oa_response_to_research_paper(work) for work in data['results']]
    unique_papers = list({paper.open_alex_id: paper for paper in papers}.values())
    if published_in:
        unique_papers = get_filtered_by_sjr_papers(published_in, unique_papers)
    #relevant_papers = rank_documents(query, unique_papers)
    if len(unique_papers) == 0:
        logger.info(f"No relevant papers found")
    return unique_papers


def get_filtered_by_sjr_papers(published_in, papers):
    filtered_papers = []
    for paper in papers:
        try:
            publisher_ids = get_publisher_id_list(published_in, "source_id")
            if paper.oa_url and paper.oa_url.endswith(".pdf") and paper.publication_id and publisher_ids.get(
                    paper.publication_id, None):
                setattr(paper, "publication_quartile", publisher_ids[paper.publication_id])
                filtered_papers.append(paper)
                logger.info("Fetched relevant papers")
                return filtered_papers
        except Exception as e:
            raise (f"Error processing paper: {e}")




