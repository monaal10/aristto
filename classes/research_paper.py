import logging
import random

from extract_figures import get_figures_and_tables

logger = logging.getLogger(__name__)


class ResearchPaper:

    def __init__(self, work):
        self.user_id = self.fetch_user_id()
        self.search_id = self.create_search_id()
        self.open_alex_id = self.fetch_id(work['id'])
        self.title = work['title']
        self.authors = self.fetch_authors(work)
        self.abstract = self.recover_abstract(work)
        self.publication_year = work['publication_year']
        self.publication_date = work['publication_date']
        self.referenced_works_ids = self.fetch_id_for_referenced_works(work)
        self.referenced_works_count = work['referenced_works_count']
        self.oa_url = "" if work['open_access']['oa_url'] is None else work['open_access']['oa_url']
        self.concepts = self.fetch_concepts(work)
        self.cited_by_count = work['cited_by_count']
        self.cited_by_url = work['cited_by_api_url']
        self.biblio = work['biblio']
        self.institutions = self.fetch_institutions(work)
        self.key_words = self.fetch_keywords(work)
        self.primary_topic = work['primary_topic']['display_name']
        self.publication = self.fetch_publication_name(work)
        self.extracted_figures = []
        self.referenced_papers = []
        self.embeddings = []

    @staticmethod
    def fetch_id(paper_id):
        # Implement the logic to extract the ID from the ID string
        w_index = paper_id.find('W')
        return paper_id[w_index:]

    @staticmethod
    def fetch_authors(work):
        authors = []
        if work['authorships']:
            for j in work['authorships']:
                authors.append(j['author']['display_name'])
        return authors

    @staticmethod
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

    @staticmethod
    def fetch_id_for_referenced_works(work):
        referenced_paper_ids = work['referenced_works']
        stripped_ids = []
        for referenced_paper_id in referenced_paper_ids:
            stripped_ids.append(ResearchPaper.fetch_id(referenced_paper_id))
        return stripped_ids

    @staticmethod
    def fetch_concepts(work):
        concepts = []
        if len(work['concepts']) > 0:
            for i in work['concepts']:
                if i['score'] >= 0.75:
                    concepts.append(i['display_name'])
        return concepts

    @staticmethod
    def fetch_keywords(work):
        keywords = []
        if len(work['keywords']) > 0:
            for i in work['keywords']:
                keywords.append(i['display_name'])
        return keywords[:3]

    @staticmethod
    def fetch_institutions(work):
        institutions = []
        if work['authorships']:
            for i in work['authorships']:
                for j in i['institutions']:
                    institutions.append(j['display_name'])
        return institutions

    @staticmethod
    def create_search_id():
        return random.randint(1000000, 9999999)

    @staticmethod
    def fetch_user_id():
        return " "

    @staticmethod
    def fetch_publication_name(work):
        if work['primary_location'] and work['primary_location']['source']:
            return work['primary_location']['source']['display_name']
        return " "

    @staticmethod
    def fetch_figures(research_paper):
        url = research_paper.oa_url
        if url and url != "":
             get_figures_and_tables(url)
        return research_paper
