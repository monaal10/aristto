import uuid

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

from main.utils.publication_filter import apply_publication_filter

from main.utils.convert_data import convert_index_response_to_research_paper

endpoint = "https://openalex-data.search.windows.net"
index_name = "paper-metadata-index"
api_key = "obCo9yVMqG5BCnWrVoaSj5owR6DelBTPOTkXcDciegAzSeDVcsKa"
credential = AzureKeyCredential(api_key)
search_client = SearchClient(endpoint, index_name, credential)

def create_filter_string(start_year: int = None, end_year: int = None,
           citation_count: int = None, published_in: list[str] = None, authors: list[str] = None, dois: list[str] = None,
                         is_deep_research: bool = None):
    try:
        filter_conditions = []

        if start_year is not None and len(str(start_year)) > 0:
            filter_conditions.append(f"publication_year ge {start_year}")
        if end_year is not None and len(str(end_year)) > 0 :
            filter_conditions.append(f"publication_year le {end_year}")
        if citation_count is not None:
            filter_conditions.append(f"cited_by_count gt {citation_count}")

        """if published_in and len(published_in) > 0:
            published_in_query = " or ".join(f'"{term}~1"' for term in published_in)
            filter_conditions.append(
                "search.ismatch(" + published_in_query + ", 'primary_location/source/display_name', 'full', 'any')"
            )"""
        if authors and len(authors) > 0:
            authors_query = " or ".join(f'"{author}"' for author in authors)
            filter_conditions.append(
                f"search.ismatch('{authors_query}', 'authorships/author/display_name', 'full', 'any')")
        if dois and len(dois) > 0:
            doi_conditions = []
            for doi in dois:
                # Escape any special characters in the DOI
                escaped_doi = doi.replace("'", "''").replace("\\", "\\\\")
                doi_conditions.append(f"doi eq '{escaped_doi}'")
            filter_conditions.append("(" + " or ".join(doi_conditions) + ")")
        if is_deep_research == True:
            filter_conditions.append(f"referenced_works_count gt {80}")
        filter_str = " and ".join(filter_conditions) if filter_conditions else None
        return filter_str
    except Exception as e:
        raise Exception(e)


def search(query: str, start_year: int = None, end_year: int = None,
           citation_count: int = None, published_in: list[str] = None, authors: list[str] = None, dois: list[str]=None,
           is_deep_research: bool = None) -> list[dict]:
    try:
        filter_str = create_filter_string(start_year, end_year, citation_count, published_in, authors, dois, is_deep_research)
        if dois and len(dois) > 0:
            results = search_client.search(
                search_text="*",  # Wildcard to match all documents, filtering will be done by DOI
                filter=filter_str,
                select="*",
                top=len(dois)  # Ensure we get all matching DOIs
            )
        else:
            results = search_client.search(
                search_text=query,
                filter=filter_str,
                query_type="semantic",
                semantic_configuration_name="abstract",
                search_fields=["title", "abstract"],
                select="*",
                top=50
            )

        documents = [doc for doc in results]
        return documents
    except Exception as e:
        raise Exception(e)


def get_relevant_papers_from_open_alex(query, start_year, end_year, citation_count, authors, published_in, sjr, dois, is_deep_research):
    try:
        results = search(
            query,
            start_year=start_year,
            end_year=end_year,
            citation_count=citation_count,
            published_in=published_in,
            authors=authors,
            dois= dois,
            is_deep_research=is_deep_research
        )
        documents = [{
                    "uuid": uuid.uuid4(),
                    "text": result.get("abstract", ""),
                    "score": result.get("@search.score", 0),
                    "paper_metadata": convert_index_response_to_research_paper(result)}
            for result in results]
        filtered_documents = []
        for document in documents:
           paper = document["paper_metadata"]
           if apply_publication_filter(paper, published_in, sjr):
               filtered_documents.append(document)
               documents.remove(document)
        return filtered_documents, documents
    except Exception as e:
        raise Exception(e)




def get_referenced_papers(paper_ids, theme):
    try:
        if paper_ids and len(paper_ids) > 0:
            id_filter = f"search.in(work_id, '{','.join([str(id) for id in paper_ids])}')"
            citation_filter = f"cited_by_count ge {10}"
            filter_str = f"({id_filter}) and ({citation_filter})"

            results = search_client.search(
                search_text=theme,
                filter=filter_str,
                select="*",
                query_type="semantic",
                semantic_configuration_name="abstract",
                search_fields=["title", "abstract"],
                top=10
            )

            documents = [doc for doc in results]
            final_documents = [{
                "uuid": uuid.uuid4(),
                "text": document.get("abstract", ""),
                "score": document.get("@search.score", 0),
                "paper_metadata": convert_index_response_to_research_paper(document)}
                for document in documents]
            return final_documents
        return []
    except Exception as e:
        raise Exception(e)



