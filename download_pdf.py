import logging
import io
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import sent_tokenize
from get_openai_embeddings import get_embedding,calculate_similarity
from extract_figures import download_pdf

import threading
import PyPDF2
import nltk
import time
import uuid
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Function to extract text from PDF content
nltk.download('punkt')

def extract_text_from_pdf(pdf_content):
    text = ""
    pdf_stream = io.BytesIO(pdf_content)
    reader = PyPDF2.PdfReader(pdf_stream)
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to split text into chunks
def chunk_text(text, chunk_size=100):
    words = text.split()
    chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

# Function to get the most relevant chunks using TF-IDF and cosine similarity
def get_relevant_chunks_embeddings(pdf_content, query, chunk_size=100, top_n=3):
    try:
        text = extract_text_from_pdf(pdf_content)
        chunks = chunk_text(text,chunk_size)
        query_embedding = get_embedding(query)
        chunk_embeddings = [get_embedding(chunk) for chunk in chunks]
        valid_chunks = [(chunk, embedding) for chunk, embedding in zip(chunks, chunk_embeddings) if embedding]

        if not query_embedding:
            logger.error("failed to retrieve query emedding")
            return []
        similarities = [calculate_similarity(query_embedding,chunk_embedding) for _, chunk_embedding in valid_chunks]
        sorted_chunks = sorted(zip(valid_chunks, similarities), key=lambda x: x[1], reverse=True)[:top_n]

        # Return top N chunks along with their similarity scores
        top_chunks = [(chunk, similarity) for (chunk, _), similarity in sorted_chunks]
        return top_chunks
    except Exception as e:
        logger.error(f"Error while generating chunks - {e}")
def generate_chunk_ids(top_chunks):
    top_chunks_formatted = {}
    for chunk in top_chunks:
        chunk_id = uuid.uuid4()
        top_chunks_formatted[chunk_id] = chunk
    return top_chunks_formatted
def get_relevant_chunks(pdf_content, query, chunk_size=100, top_n=3):
    text = extract_text_from_pdf(pdf_content)
    chunks = chunk_text(text, chunk_size)
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(chunks)
    query_vec = vectorizer.transform([query])
    similarity_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = similarity_scores.argsort()[-top_n:][::-1]
    top_chunks = [(chunks[i], similarity_scores[i]) for i in top_indices]
    top_chunks = generate_chunk_ids(top_chunks)
    return top_chunks

# Worker function for multithreading
def worker(urls, result_list, index):
    for url in urls:
        content = download_pdf(url)
        if content:
            result_list[index].append(content)

# Function to download PDFs using multiple threads
def download_pdfs_from_urls(urls):
    result = []
    for url in urls:
        if url.endswith(".pdf"):
            logger.info(f"Downloading from {url}")
            result.append(download_pdf(url))
        else:
            logger.error(f"Cannot Download non pdf url - {url}")
    return result

# The goal is to generate and store chunks of the pdfs that are will be downloaded
# Hence this is the single point of entry for that whole process
def generate_chunks(urls, user_query, chunk_size=100, top_n=3):
    logger.info("Starting PDF download process.")
    pdfs = download_pdfs_from_urls(urls) 
    logger.info(f"Downloaded {len(pdfs)} PDFs. Extracting relevant chunks for the query.")
    if not pdfs:
        logger.error("pdfs iterable didnt exist in generate_chunks()")
    for pdf_content in pdfs:
        relevant_chunks = get_relevant_chunks(pdf_content, user_query, chunk_size, top_n)
    for chunk_id,chunk in relevant_chunks.items():
        logger.info(f"{chunk_id} - {chunk}")
    return relevant_chunks

 