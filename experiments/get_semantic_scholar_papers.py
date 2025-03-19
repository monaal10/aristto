import io

import PyPDF2
import requests

from modules.relevant_papers_module import get_relevant_papers, get_publisher_id_list
from utils.convert_data import convert_ss_response_to_research_paper


def create_hhtp_url_for_ss(query, start_year, end_year, citation_count, published_in, isLitReview):
    initial_string = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&fields=title,url,corpusId,abstract,authors,publicationVenue,citationCount,year"
    if start_year or end_year:
        if not start_year:
            start_year = ""
        if not end_year:
            end_year = ""
        initial_string += f"&year={str(start_year)}-{str(end_year)}"
    if citation_count:
        initial_string += f"&minCitationCount={str(citation_count)}"
    if published_in and len(published_in) > 0:
        venue_string = ''
        for venue in published_in:
            venue_string += venue + ','
        initial_string += f"&venue={venue_string[:len(venue_string)-1]}"
    if isLitReview:
        initial_string += f"&publicationTypes=JournalArticle,MetaAnalysis"
    return initial_string + "&limit=100"




def get_ss_papers(query, start_year, end_year, citation_count, published_in, authors, isLitReview):
    filtered_papers = []
    headers = {
        "x-api-key": "vd5G9VoPYk3hfCYyPjZR334dvZCumbEF2tkdeQhK",
    }
    http_url = create_hhtp_url_for_ss(query, start_year, end_year, citation_count, published_in, isLitReview)
    response = requests.get(http_url)
    data = response.json().get("data")
    papers = []
    for paper in data:
        papers.append(convert_ss_response_to_research_paper(paper))
    return papers


#x = get_ss_papers("What are some of the best methods to detect deepfakes?", None, None, 0, None)
#print()
headers = {
    "x-api-key": "vd5G9VoPYk3hfCYyPjZR334dvZCumbEF2tkdeQhK",
}
response = requests.get("https://api.semanticscholar.org/datasets/v1/release/latest/dataset/paper-ids")
print(response.text)
