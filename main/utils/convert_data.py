import logging
import random
import re

import requests

from classes.research_paper import ResearchPaper

logger = logging.getLogger(__name__)


def convert_mongodb_to_research_paper(paper):
    try:
        response = ResearchPaper()
        for key in paper.keys():
            response[key] = paper[key]
        return response
    except Exception as e:
        raise f"Could not convert mongoDB response to research paper: {e}"


def convert_oa_response_to_research_paper(work):
    try:
        user_id = fetch_user_id()
        search_id = create_search_id()
        open_alex_id = fetch_id(work['id'])
        title = work['title']
        authors = fetch_authors(work)
        abstract = recover_abstract(work)
        publication_year = work['publication_year']
        publication_date = work['publication_date']
        referenced_works_ids = fetch_id_for_referenced_works(work)
        referenced_works_count = work['referenced_works_count']
        oa_url = fetch_oa_url(work)
        concepts = fetch_concepts(work)
        cited_by_count = work['cited_by_count']
        cited_by_url = work['cited_by_api_url']
        biblio = work['biblio']
        institutions = fetch_institutions(work)
        key_words = fetch_keywords(work)
        primary_topic = fetch_primary_topic(work)
        publication = fetch_publication_name(work)
        publication_id = fetch_publication_id(work)
        # summary = get_summary_reference(extract_doi(work['doi'])) if work['doi'] else ""
        return ResearchPaper(user_id=user_id, search_id=search_id, open_alex_id=open_alex_id, title=title,
                             authors=authors, abstract=abstract, publication_year=publication_year,
                             publication_date=publication_date, referenced_works_ids=referenced_works_ids,
                             referenced_works_count=referenced_works_count, oa_url=oa_url, concepts=concepts,
                             cited_by_count=cited_by_count, cited_by_url=cited_by_url, biblio=biblio,
                             institutions=institutions, key_words=key_words, primary_topic=primary_topic,
                             publication=publication, publication_id=publication_id
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
        stripped_ids.append(fetch_id(referenced_paper_id))
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
        work['best_oa_location'][
            'pdf_url']


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
