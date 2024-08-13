from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import torch
from typing import List

# Initialize the embedding model
model = SentenceTransformer("Alibaba-NLP/gte-large-en-v1.5", trust_remote_code=True)
device = "mps" if torch.backends.mps.is_available() else "cpu"
model.to(device)
def get_embedding(text):
    embedding = model.encode(text, device=device, convert_to_tensor=True)
    return embedding

def calculate_similarity_scores(query_embedding, paper_embeddings):
    similarities = [
        calculate_similarity(query_embedding, doc_embedding)
        for doc_embedding in paper_embeddings
    ]
    return similarities

def calculate_similarity(query_embedding: List[float], document_embedding: List[float]) -> float:
    """
    Calculate the cosine similarity between two embeddings.

    :param query_embedding: The embedding of the query
    :param document_embedding: The embedding of a document
    :return: The cosine similarity score
    """
    return cosine_similarity(query_embedding.reshape(1,-1), document_embedding.reshape(1,-1))[0][0]