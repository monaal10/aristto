import requests

def fetch_paper_details_from_semantic_scholar(doi_id):
    try:
        # Define the Semantic Scholar API URL
        semantic_scholar_url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi_id}?fields=title,abstract,references"

        # Make a request to Semantic Scholar
        response = requests.get(semantic_scholar_url)
        response.raise_for_status()  # Raise an error if the request was unsuccessful

        # Parse the JSON response
        paper_data = response.json()

        # Extract the paper's summary (abstract) and references
        summary = paper_data.get('abstract', 'No summary available.')
        references = paper_data.get('references', [])

        return {
            "summary": summary,
            "references": references
        }

    except Exception as e:
        print(str(e))
        # logger.error(f"Error fetching data from Semantic Scholar: {str(e)}")
        return None
