import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict
import math
from collections import Counter
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.pdf_operations import download_pdfs_parallel

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Function to split text into chunks
def chunk_text(paper):
    try:
        if paper.pdf_content_chunks:
            return paper
        paper_text = paper.pdf_content
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=50,
            length_function=len,
            is_separator_regex=False,
        )
        chunks = {}
        texts = text_splitter.create_documents([paper_text])
        for i in range(len(texts)):
            chunks[paper.open_alex_id + "_" + str(i)] = texts[i].page_content
        paper.pdf_content_chunks = chunks
        return paper
    except Exception as e:
        raise f"Could not chunk text: {e}"


def parallel_chunk_text(papers):
    final_papers = []
    with ProcessPoolExecutor(max_workers=8) as executor:  # Adjust number of workers based on CPU capacity
        futures = {executor.submit(chunk_text, paper): paper for paper in papers}
        for future in as_completed(futures):
            paper = future.result()
            final_papers.append(paper)
    return final_papers


def parallel_download_and_chunk_papers(papers):
    papers_with_pdf_content = download_pdfs_parallel(papers)
    final_papers = parallel_chunk_text(papers_with_pdf_content)
    return final_papers


def preprocess_text(text: str) -> List[str]:
    try:
        """
        Preprocess text by converting to lowercase, removing punctuation and splitting into words
        """
        # Convert to lowercase and remove punctuation
        text = re.sub(r'[^\w\s]', '', text.lower())
        # Split into words
        return text.split()
    except Exception as e:
        raise f"Could not preprocess text: {e}"



def get_relevant_chunks(query: str, papers, k1: float = 1.5, b: float = 0.75):
    try:

        # Preprocess query
        query_terms = preprocess_text(query)

        # Flatten all chunks into a list of documents for BM25 calculation
        all_chunks = []
        chunk_metadata = []  # Store original id and chunk_id

        for paper in papers:
            doc_id = paper.open_alex_id
            if paper.pdf_content_chunks:
                for chunk_id, chunk_text in paper.pdf_content_chunks.items():
                    all_chunks.append(preprocess_text(chunk_text))
                    chunk_metadata.append({
                        'doc_id': doc_id,
                        'chunk_id': chunk_id,
                        'text': chunk_text,
                        'title': paper.title,
                        'summary': paper.summary,
                    })

        # Calculate document frequencies
        N = len(all_chunks)
        doc_freqs = Counter()
        for chunk in all_chunks:
            # Count each term only once per document
            doc_freqs.update(set(chunk))

        # Calculate average document length
        avg_doc_length = sum(len(chunk) for chunk in all_chunks) / N

        # Calculate BM25 scores for each chunk
        results = []
        for idx, (chunk_words, metadata) in enumerate(zip(all_chunks, chunk_metadata)):
            score = 0.0
            doc_length = len(chunk_words)

            # Count terms in current document
            term_freqs = Counter(chunk_words)

            for term in query_terms:
                if term in doc_freqs:
                    # Calculate IDF component
                    idf = math.log((N - doc_freqs[term] + 0.5) / (doc_freqs[term] + 0.5) + 1.0)

                    # Calculate TF component with BM25 scaling
                    tf = term_freqs[term]
                    tf_component = ((k1 + 1) * tf) / (k1 * (1 - b + b * doc_length / avg_doc_length) + tf)

                    score += idf * tf_component

            if score > 0:  # Only include chunks with non-zero scores
                results.append({
                    'paper_id': metadata['doc_id'],
                    'chunk_id': metadata['chunk_id'],
                    'chunk_text': metadata['text'],
                    'title': metadata['title'],
                    'score': score
                })

        # Sort results by score in descending order
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    except Exception as e:
        raise f"Could not get relevant chunks: {e}"
