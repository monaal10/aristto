import requests
import logging

from utils.convert_data import convert_oa_response_to_research_paper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_referenced_papers(original_paper):
    open_alex_url = "https://api.openalex.org/works?mailto=monaalsanghvi1998@gmail.com&filter=openalex_id:"
    referenced_papers = []
    sort_suffix = "&sort=cited_by_count:desc"
    try:
        logger.info("Getting referenced papers")
        if len(original_paper["referenced_works_ids"]) > 0:
            for referenced_work in original_paper["referenced_works_ids"][:99]:
                open_alex_url += referenced_work + "|"
            response = requests.get(open_alex_url[:-2] + sort_suffix)
            data = response.json()
            for referenced_work_data in data['results'][:4]:
                referenced_papers.append(vars(convert_oa_response_to_research_paper(referenced_work_data)))
    except Exception:
        raise ("Error while getting referenced papers")
    return referenced_papers