import openai
from sklearn.metrics.pairwise import cosine_similarity
from typing import List

import pandas as pd
from classes import research_paper


# Set up the OpenAI API client
openai.api_key = "sk-zFNU8L6Nkc1e-2VgAKoSB8tBcuEgJ140flDuDTc0muT3BlbkFJ_ChBKzjg63-HOPaPNczEzxWVoahtCUU9g1ZsZzBvgA"
openai_model = "text-embedding-3-small"
def get_embedding(text: str, model: str = openai_model, max_retries: int = 3) -> List[float]:
    """
   Get an embedding for the given text using the specified OpenAI model.
   Retries with halved text length on failure.


   :param text: The input text to embed
   :param model: The name of the OpenAI embedding model to use
   :param max_retries: Maximum number of retries
   :return: A list of floats representing the embedding
   """
    for attempt in range(max_retries):
        try:
            response = openai.embeddings.create(
                input=[text],
                model=model
            )
            return response.data[0].embedding
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Max retries reached. Final error: {e}")
                return []

            print(f"Attempt {attempt + 1} failed: {e}")
            text = text[:len(text) // 2]  # Halve the text length
            print(f"Retrying with text length: {len(text)}")

    return []


def calculate_similarity(query_embedding: List[float], document_embedding: List[float]) -> float:
    """
   Calculate the cosine similarity between two embeddings.


   :param query_embedding: The embedding of the query
   :param document_embedding: The embedding of a document
   :return: The cosine similarity score
   """
    return cosine_similarity([query_embedding], [document_embedding])[0][0]
def get_publisher_id_list(publisher_ranks):
    publisher_ids = {}

    df = pd.read_csv('journal_quartile_rank.csv')
    df1 = pd.read_csv('/Users/monaal/Downloads/rankings_final_with_ids.csv')
    df1_ids = df1['ids'].to_list()
    df_final = pd.DataFrame()
    for publisher_rank in publisher_ranks:
        df_filtered = df[df['SJR Best Quartile'] == publisher_rank]
        df_final = pd.concat([df_final, df_filtered], ignore_index=True)

    for i in range(len(df_final)):
        publisher_ids[df_final['source_id'][i]] = df_final['SJR Best Quartile'][i]
    for j in df1_ids:
        if type(j) == str:
            publisher_ids[j] = df1_ids
    return publisher_ids



def rank_documents(query: str, documents: List[research_paper]):
    """
   Rank documents based on their similarity to the query.


   :param query: The query string
   :param documents: A list of document strings
   :return: A list of tuples containing (document, similarity_score), sorted by similarity in descending order
   """
    # Get embeddings
    query_embedding = get_embedding(query)
    document_embeddings = []
    for paper in documents:
            paper_text = f"{paper.title} {' '.join(paper.authors)} {paper.abstract}"
            paper_embedding = get_embedding(paper_text)
            document_embeddings.append(paper_embedding)
            paper.embeddings = paper_embedding
            #paper.pdf_content = io.BytesIO(download_pdf(paper.oa_url))

    # Calculate similarities
    similarities = [
        calculate_similarity(query_embedding, doc_embedding)
        for doc_embedding in document_embeddings
    ]

    # Create a list of (document, similarity) tuples and sort by similarity
    ranked_documents = sorted(
        zip(documents, similarities),
        key=lambda x: x[1],
        reverse=True
    )

    return [doc for doc, _ in ranked_documents]
