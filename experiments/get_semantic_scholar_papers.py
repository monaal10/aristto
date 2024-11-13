import requests

from modules.relevant_papers_module import get_relevant_papers, get_publisher_id_list


def get_ss_papers(query, start_year, end_year, citation_count, published_in):
    filtered_papers = []
    headers = {
        "x-api-key": "vd5G9VoPYk3hfCYyPjZR334dvZCumbEF2tkdeQhK",
    }
    response = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&"
                            f"fields=title,url,abstract,authors,publicationVenue&isOpenAccess=true&minCitationCount="
                            f"{citation_count}&year={str(start_year) + "-" + str(end_year)}&offset=100&limit=100", headers=headers)
    data = response.json().get("data")
    paper_names = [paper.get("title") for paper in data]
    publisher_ids = get_publisher_id_list(published_in, "ss_id")
    for paper in data:
        if paper["publicationVenue"] and paper["publicationVenue"]["id"] in publisher_ids:
            filtered_papers.append(paper)
    return filtered_papers


get_ss_papers("deepfake detection", 2010, 2024, 0, ["Q1, Q2"])
get_relevant_papers("deepfake detection", 2010, 2024, 0, ["Q1", "Q2"], None)

