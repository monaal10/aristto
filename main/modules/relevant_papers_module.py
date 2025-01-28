from json import JSONDecodeError

import requests
from pyalex import Institutions, Authors
import pyalex
import logging
from main.classes.research_paper import ResearchPaper
# from embeddings_module import rank_documents
import pandas as pd
from rapidfuzz import process
from main.utils.convert_data import convert_oa_response_to_research_paper
from main.modules.embeddings_module import rank_documents
from main.utils.convert_data import convert_ss_response_to_research_paper
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
            for author in authors:
                try:
                    response = requests.get("https://api.openalex.org/authors?search=" + author)
                    data = response.json()
                    logger.info(data)
                    if len(data["results"]) > 0:
                        author_list.append(data["results"][0]["id"])
                except JSONDecodeError:
                    logger.error("Unable to get Author id")

        for author in author_list:
            id = author.split(".org/")
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
            if len(author_ids) > 0:
                http_url = http_url + ',author.id:' + author_ids
            else:
                return ""

        http_url = http_url + "&sort=relevance_score:desc&per-page=200&page="
        return http_url
    except Exception as e:
        raise f"Could not form http url from given parameters: {e}"





def create_hhtp_url_for_ss(query, start_year, end_year, citation_count, published_in):
    try:
        initial_string = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&fields=title,openAccessPdf,abstract,authors,publicationVenue,citationCount,year"
        if start_year or end_year:
            if not start_year:
                start_year = ""
            if not end_year:
                end_year = ""
            initial_string += f"&year={str(start_year)}-{str(end_year)}"
        if citation_count:
            initial_string += f"&minCitationCount={str(citation_count)}"
        if published_in and len(published_in) > 0:
            initial_string += f"&venue={published_in}"
        return initial_string + "&limit=100"
    except Exception as e:
     raise f"Could not form semantic scholar hhtp url from given parameters: {e}"




def get_ss_papers(query, start_year, end_year, citation_count, published_in):
    headers = {
        "x-api-key": "vd5G9VoPYk3hfCYyPjZR334dvZCumbEF2tkdeQhK",
    }
    http_url = create_hhtp_url_for_ss(query, start_year, end_year, citation_count, published_in)
    response = requests.get(http_url)
    data = response.json().get("data")
    papers = []
    if data:
        for paper in data:
            papers.append(convert_ss_response_to_research_paper(paper))
    return papers


def get_sjr_rank_fuzzy_search(journal_names, threshold=80):
    try:

        df = pd.read_csv('main/modules/jqr.csv')
        for journal in journal_names:
            # Find the closest match in the 'title' column
            best_match, score, temp = process.extractOne(journal, df['title'])

            # If the match score is above the threshold, we consider it a valid match
            if score >= threshold:
                # Retrieve the corresponding SJR value
                sjr_value = df[df['title'] == best_match]['sjr'].values[0]
                return sjr_value
        return ''
    except Exception as e:
        raise e


def get_relevant_papers(query, start_year, end_year, citation_count, published_in, authors):
    try:
        #http_url = create_http_url_for_open_alex(query, start_year, end_year, citation_count, published_in,authors)
        http_url = create_hhtp_url_for_ss(query, start_year, end_year, citation_count, published_in)
        if len(http_url) == 0:
            return []
        response = requests.get(http_url)
        #data = response.json()
        #papers = [convert_oa_response_to_research_paper(work) for work in data['results']]

        data = response.json().get("data")
        if data:
            papers = [convert_ss_response_to_research_paper(work) for work in data]
            unique_papers = list({paper.open_alex_id: paper for paper in papers}.values())
            filtered_papers = []
            for paper in unique_papers:
                if paper.publication:
                    publication_names = paper.publication_alternate_names + [paper.publication]
                    sjr = get_sjr_rank_fuzzy_search(publication_names)
                    if sjr == "Q1":
                        filtered_papers.append(paper)

            #relevant_papers = rank_documents(query, unique_papers)
            if len(unique_papers) == 0:
                logger.info(f"No relevant papers found")
            return filtered_papers
        return []
    except JSONDecodeError:
        return []

    except Exception as e:
        raise e


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




