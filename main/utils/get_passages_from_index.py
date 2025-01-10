from qdrant_client import QdrantClient
from transformers import AutoModel, AutoTokenizer
import torch
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

def get_embedding(text, model_name="avsolatorio/NoInstruct-small-Embedding-v0"):
    """
    Generate embeddings for input text using the specified model
    """
    # Initialize tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    # Tokenize and get model inputs
    inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt")

    # Generate embeddings
    with torch.no_grad():
        outputs = model(**inputs)
        # Use mean pooling of the last hidden state
        embeddings = outputs.last_hidden_state.mean(dim=1)

    # Convert to numpy array and normalize
    embedding = embeddings[0].numpy()
    embedding = embedding / np.linalg.norm(embedding)

    return embedding




def optimized_search(query, collection_name="embeddings_collection", limit=5):

    # Get query vector
    query_vector = get_embedding(query)

    # Optimized search parameters
    search_params = rest.SearchParams(
        hnsw_ef=128,  # Lower for faster search
        exact=False
    )
    client = QdrantClient("localhost", port=6333)

    # Perform search with corrected parameters
    search_result = client.search(
        collection_name=collection_name,
        query_vector=query_vector.tolist(),
        limit=limit,
        search_params=search_params,
        score_threshold=0.7,
        with_payload=True,  # Simply get all payload
        with_vectors=False
    )

    return search_result


if __name__ == "__main__":
    query = "what are deepfakes?"
    results = optimized_search(query)

    print(f"\nQuery: {query}\n")
    print("Search Results:")
    for i, hit in enumerate(results, 1):
        print(f"\n{i}. Score: {hit.score:.4f}")
        print(f"Text: {hit.payload.get('text', '')[:200]}...")