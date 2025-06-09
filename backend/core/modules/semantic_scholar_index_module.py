import logging
import uuid
from json import JSONDecodeError

import requests
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents._generated.models import VectorizedQuery
from transformers import AutoTokenizer, AutoModel
import torch

from main.utils.publication_filter import apply_publication_filter
from main.utils.convert_data import convert_oa_response_to_research_paper
import boto3

from main.modules.open_alex_index_module import get_relevant_papers_from_open_alex

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load the tokenizer and model to compute embeddings.
tokenizer = AutoTokenizer.from_pretrained("avsolatorio/NoInstruct-small-Embedding-v0")
model = AutoModel.from_pretrained("avsolatorio/NoInstruct-small-Embedding-v0")


dynamodb = boto3.client('dynamodb', aws_access_key_id='AKIA6ODU27KHMGRMPHOZ', aws_secret_access_key=
        '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', region_name='us-east-1')



def compute_embedding(text):
    try:
        """
        Compute an embedding vector for the provided text using the Hugging Face model.
        The function uses mean pooling over the token embeddings.
        """
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        # Mean pooling: average over the token embeddings.
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()
        return embedding
    except Exception as e:
        raise Exception(f"Could not compute embeddings {e}")

def get_relevant_texts(query):
    try:
        # update index to have all the filters.
        endpoint = "https://aristto-embeddings-search.search.windows.net"
        index_name = "azureblob-index"
        api_key = "X8o3QQDGvbhFjtGHlpoo5GvYFKvdDGIUUHIGjlkaQzAzSeArHAAx"

        # Create the SearchClient instance.
        search_client = SearchClient(endpoint=endpoint,
                                     index_name=index_name,
                                     credential=AzureKeyCredential(api_key))
        vector_query = VectorizedQuery(vector=compute_embedding(query), fields="embeddings", k_nearest_neighbors=50)
        results = search_client.search(
            search_text=query,
            vector_queries=[vector_query],
            select=["id", "text"],
            query_type="semantic",
            semantic_configuration_name="relevant-texts",
            top=100,
        )

        # Extract and return the relevant fields from each document.
        output = []
        for result in results:
            output.append({
                "uuid": uuid.uuid4(),
                "id": result.get("id"),
                "text": result.get("text", ""),
                "score": result.get("@search.score", 0),
            })
        return output
    except Exception as e:
        raise Exception(f"Could not get relevant texts from azure index{e}")


def get_doi_ids(documents):
    try:
        paper_ids = [f"{document.get("id")}" for document in documents]
        # Initialize the DynamoDB client

        table_name = 'ss-id-to-publication-id'

        # Construct a list of key dictionaries for each id in the input list.
        # Here, we assume that "corpusid" is the primary key and its type is String.
        keys = [{'corpusid': {'S': str(id_val)}} for id_val in set(paper_ids)]


        # Use BatchGetItem to fetch items from the table.
        # Note: BatchGetItem can retrieve up to 100 items at a time.
        response = dynamodb.batch_get_item(
            RequestItems={
                table_name: {
                    'Keys': keys,
                    'ProjectionExpression': 'doi, corpusid'
                }
            }
        )

        # Process the response to extract corpusid and doi values.
        items = response.get('Responses', {}).get(table_name, [])
        results = []
        for document in documents:
            for item in items:
                if item.get('doi', {}).get('S') is not None and item.get('corpusid', {}).get('S') == document['id']:
                    document['doi'] = item.get('doi', {}).get('S')
                    results.append(document)
        return results
    except Exception as e:
        raise Exception("Could not get doi ids {e}")


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
        raise Exception(f" Could not get author ids from openAlex : {e}")


def get_paper_details_from_oa(documents, start_year, end_year, citation_count, authors, publication_names, sjr):
    try:
        paper_ids = [document.get("doi") for document in documents]
        author_ids = get_author_id_list(authors) if authors else None
        cited_by_count = citation_count if citation_count else 0
        start_year_final = (str(start_year) if start_year else "1800")
        end_year_final = (str(end_year) if end_year else "2024")
        paper_ids_string = "|".join(paper_ids)
        http_url = ('https://api.openalex.org/works?filter=doi:' +
                    paper_ids_string + ',cited_by_count:>' + str(
                    cited_by_count) + ',publication_year:>' + start_year_final + ',publication_year:<' + end_year_final)
        if author_ids and len(author_ids) > 0:
                http_url = http_url + ',author.id:' + author_ids
        response = requests.get(http_url)
        data = response.json()['results']
        papers = [convert_oa_response_to_research_paper(paper) for paper in data]
        filtered_papers = []
        for paper in data[:]:
            converted_paper = convert_oa_response_to_research_paper(paper)
            if apply_publication_filter(converted_paper, publication_names, sjr):
                for document in documents:
                    if document.get("doi") == converted_paper.doi:
                        document['paper_metadata'] = converted_paper
                        if paper in data:
                            data.remove(paper)
                        filtered_papers.append(document)
        return filtered_papers, papers
    except Exception as e:
        raise Exception("Could not get paper metadata {e}")


def get_papers_from_semantic_scholar(query, start_year, end_year, citation_count, authors, publication_names, sjr):
    try:
        documents = get_relevant_texts(query)
        documents_with_doi_ids = get_doi_ids(documents)
        doi_ids = [doc["doi"] for doc in documents_with_doi_ids]
        filtered_documents_with_paper_metadata, documents_with_paper_metadata = get_relevant_papers_from_open_alex(
            query, start_year, end_year, citation_count, authors, publication_names, sjr, doi_ids, False)
        for filtered_document in filtered_documents_with_paper_metadata:
            for document in documents_with_doi_ids:
                if document.get("doi") == filtered_document.get("paper_metadata"):
                    filtered_document["text"] = document["text"]
        return filtered_documents_with_paper_metadata, documents_with_paper_metadata
    except Exception as e:
        raise Exception(f"Could not get context {e}")

