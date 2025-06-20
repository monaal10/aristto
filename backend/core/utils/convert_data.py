import logging
import random
import re

import requests

from main.classes.research_paper import ResearchPaper

logger = logging.getLogger(__name__)

def convert_index_response_to_research_paper(index_response):
      try:
        user_id = fetch_user_id()
        open_alex_id = fetch_id(index_response.get('work_id'))
        title = index_response.get('title')
        abstract = index_response.get('abstract')
        publication_year = index_response.get('publication_year')
        cited_by_count = index_response.get('cited_by_count')
        authors = fetch_authors(index_response)
        publication = fetch_publication_name(index_response)
        oa_url, isPdfUrl = fetch_pdf_url(index_response)
        doi = fetch_doi_from_index(index_response)
        referenced_works_ids = index_response['referenced_works']

        return ResearchPaper(user_id=user_id, open_alex_id=open_alex_id, title=title,
                             authors=authors, abstract=abstract, publication_year=publication_year,
                             referenced_works_ids=referenced_works_ids, oa_url=oa_url,
                             cited_by_count=cited_by_count, publication=publication, doi=doi, isPdfUrl=isPdfUrl
                             )
      except Exception as e:
        raise f"Could not convert index response to research paper: {e}"


def convert_ss_response_to_research_paper(ss_response):
    try:
        user_id = fetch_user_id()
        open_alex_id = str(ss_response.get('corpusId'))
        title = ss_response.get('title')
        abstract = ss_response.get('abstract')
        publication_year = ss_response.get('year')
        cited_by_count = ss_response.get('citationCount')
        authors = fetch_authors_from_ss_response(ss_response.get('authors'))
        publication, publication_id, alternate_names = fetch_publication_from_ss_response(ss_response.get('publicationVenue'))
        oa_url = fetch_pdf_url_from_ss_response(ss_response.get('openAccessPdf'))
        return ResearchPaper(user_id=user_id, open_alex_id=open_alex_id, title=title,
                             authors=authors, abstract=abstract, publication_year=publication_year,
                             cited_by_count=cited_by_count, publication=publication, publication_id=publication_id,
                             oa_url=oa_url, publication_alternate_names=alternate_names)
    except Exception as e:
        raise f"Could not convert ss response to ResearchPaper: {e}"

def convert_mongodb_to_research_paper(paper):
    try:
        return ResearchPaper(**paper)
    except Exception as e:
        raise f"Could not convert mongoDB response to research paper: {e}"


def convert_oa_response_to_research_paper(work):
    try:
        user_id = fetch_user_id()
        open_alex_id = fetch_id(work['id'])
        title = work['title']
        authors = fetch_authors(work)
        abstract = recover_abstract(work)
        publication_year = work['publication_year']
        publication_date = work['publication_date']
        referenced_works_ids = fetch_id_for_referenced_works(work)
        referenced_works_count = work['referenced_works_count']
        oa_url, isPdfUrl = fetch_pdf_url(work)
        concepts = fetch_concepts(work)
        cited_by_count = work['cited_by_count']
        cited_by_url = work['cited_by_api_url']
        biblio = work['biblio']
        institutions = fetch_institutions(work)
        key_words = fetch_keywords(work)
        primary_topic = fetch_primary_topic(work)
        publication = fetch_publication_name(work)
        publication_id = fetch_publication_id(work)
        doi = extract_doi(work['doi']) if work['doi'] else ""
        return ResearchPaper(user_id=user_id, open_alex_id=open_alex_id, title=title,
                             authors=authors, abstract=abstract, publication_year=publication_year,
                             publication_date=publication_date, referenced_works_ids=referenced_works_ids,
                             referenced_works_count=referenced_works_count, oa_url=oa_url, concepts=concepts,
                             cited_by_count=cited_by_count, cited_by_url=cited_by_url, biblio=biblio,
                             institutions=institutions, key_words=key_words, primary_topic=primary_topic,
                             publication=publication, publication_id=publication_id, doi=doi, isPdfUrl=isPdfUrl
                             )
    except Exception as e:
        raise f"Could not convert open_alex response to research paper: {e}"


def fetch_id(paper_id):
    # Implement the logic to extract the ID from the ID string
    w_index = paper_id.find('W')
    return paper_id[w_index:]


def fetch_authors(work):
    authors = []
    if work['authorships']:
        for j in work['authorships']:
            authors.append(j['author']['display_name'])
    return authors


def recover_abstract(work):
    inverted_index = work['abstract_inverted_index']
    abstract = ''
    if inverted_index:
        abstract_size = max([max(appearances) for appearances in inverted_index.values()]) + 1

        abstract = [None] * abstract_size
        for word, appearances in inverted_index.items():
            for appearance in appearances:
                abstract[appearance] = word

        abstract = [word for word in abstract if word is not None]
        abstract = ' '.join(abstract)
    return abstract


def fetch_id_for_referenced_works(work):
    referenced_paper_ids = work['referenced_works']
    stripped_ids = []
    for referenced_paper_id in referenced_paper_ids:
        stripped_ids.append((referenced_paper_id))
    return stripped_ids


def fetch_concepts(work):
    concepts = []
    if len(work['concepts']) > 0:
        for i in work['concepts']:
            if i['score'] >= 0.75:
                concepts.append(i['display_name'])
    return concepts


def fetch_keywords(work):
    keywords = []
    if len(work['keywords']) > 0:
        for i in work['keywords']:
            keywords.append(i['display_name'])
    return keywords[:3]


def fetch_institutions(work):
    institutions = []
    if work['authorships']:
        for i in work['authorships']:
            for j in i['institutions']:
                institutions.append(j['display_name'])
    return institutions


def create_search_id():
    return random.randint(1000000, 9999999)


def fetch_user_id():
    return ""


def fetch_publication_name(work):
    if work['primary_location'] and work['primary_location']['source']:
        return work['primary_location']['source']['display_name']
    return ""


def fetch_publication_id(work):
    if work['primary_location'] and work['primary_location']['source']:
        return work['primary_location']['source']['id'].split(".org/")[1]
    return ""


def fetch_primary_topic(work):
    if work['primary_topic']:
        return work['primary_topic']['display_name']
    return ""


def fetch_oa_url(work):
    return "" if work['best_oa_location'] is None or work['best_oa_location']['pdf_url'] is None else \
        work['best_oa_location']['pdf_url']

def fetch_pdf_url(response):
    if response['primary_location'] is None or response['primary_location']['pdf_url'] is None:
        return fetch_landing_page_url(response), False
    else:
        return response['primary_location']['pdf_url'], True

def fetch_landing_page_url(response):
    return "" if response['primary_location'] is None or response['primary_location']['landing_page_url'] is None else \
        response['primary_location']['landing_page_url']

def fetch_doi_from_index(response):
    return "" if response['primary_location'] is None or response['primary_location']['doi'] is None else \
        response['primary_location']['doi']


def get_summary_reference(doi):
    # Getting Reference and summary from semantic Scholar
    try:
        url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,references,tldr"
        response = requests.get(url).json()
        return response.get("tldr", {}).get("text", "")
    except Exception as e:
        logger.error(f"Error fetching data from Semantic Scholar: {str(e)}")
        return ""


def extract_doi(doi_url):
    parts = re.split(r'/+', doi_url)

    if "doi.org" in parts:
        index = parts.index("doi.org")
        doi = "/".join(parts[index + 1:])
        return doi
    return None

def fetch_authors_from_ss_response(author_list):
    author_names =[]
    if author_list and len(author_list) > 0:
        for author in author_list:
            author_names.append(author['name'])
    return author_names

def fetch_publication_from_ss_response(publication):
    name = ''
    id = ''
    alternate_names = []
    if publication:
        name = publication['name']
        id = publication['id']
        alternate_names = publication.get("alternate_names", [])
    return name, id, alternate_names

def fetch_pdf_url_from_ss_response(openAccessPdf):
    if openAccessPdf:
        return openAccessPdf.get("url") if openAccessPdf.get("url") else ""

