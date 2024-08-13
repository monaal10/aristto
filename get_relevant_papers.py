from pyalex import Works, Authors, Sources, Institutions, Publishers, Funders
import pyalex
import datetime
import logging
import numpy as np
from classes.research_paper import ResearchPaper
from embedding_model import get_embedding, calculate_similarity_scores
from tqdm import tqdm
#from get_openai_embeddings import get_relevant_docs_from_oai

# Configure logging
logger = logging.getLogger(__name__)
pyalex.config.email = "monaalsanghvi1998@gmail.com"
min_cited_by_count = 20


def semantic_search(query, papers, top_k=75, batch_size=1):
    query_embedding = get_embedding(query).cpu().numpy()
    paper_embeddings = []

    # Get Embeddings
    logger.info("getting embeddings for each paper")

    # Process papers in batches
    for i in tqdm(range(0, min(len(papers), top_k), batch_size)):

        batch = papers[i:min(i + batch_size, top_k)]
        batch_texts = [f"{paper.title}{paper.abstract}"[:10000] for paper in batch]

        # Get embeddings for the batch
        batch_embeddings = get_embedding(batch_texts)

        # Add batch embeddings to the list
        paper_embeddings.extend(batch_embeddings.cpu())

    paper_embeddings = np.array(paper_embeddings)
    #print("time taken 2", datetime.datetime.now() - time)

    # Calculate cosine similarities
    similarities = calculate_similarity_scores(query_embedding, paper_embeddings)

    # Sort papers by similarity
    sorted_papers = sorted(zip(similarities, papers[:top_k]), key=lambda x: x[0], reverse=True)
    return [paper for _, paper in sorted_papers[:top_k]]

def get_relevant_papers(query):
    papers = []
    logger.info("Fetching works from OpenAlex")
    pages = (Works()
             .search(query)
             .filter(cited_by_count=">" + str(min_cited_by_count))
             .sort(relevance_score="desc")
             .paginate(method="page", per_page=5, n_max=1)
             )
    for page in pages:
        for work in page:
            papers.append(ResearchPaper(work))
    #print("time taken 1", datetime.datetime.now() - time)
    # relevant_papers = get_relevant_docs_from_oai(query, papers[:75])
    # Perform semantic search on the initial results
    relevant_papers = semantic_search(query, papers)
    return relevant_papers


if __name__ == "__main__":
    time = datetime.datetime.now()
    papers = get_relevant_papers("Diffusion models to create synthetic datasets")
    print([paper.title for paper in papers])
    print(len(papers))
    print("time taken 3", datetime.datetime.now() - time)
