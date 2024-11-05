import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import PyPDF2
import requests
import fitz  # PyMuPDF
import io
from PIL import Image
import base64
import requests
import threading
import PyPDF2
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Function to download a single PDF from a URL
def download_pdf(url):
    try:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.44/72.124 Safari/537.36'
        headers = {
            'User-Agent': user_agent
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes

        logger.info(f"Downloaded {url} successfully.")
        text = extract_text_from_pdf(response.content)
        return url, text  # Return URL and its content
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        return url, None  # Return None if there's an error


# Function to download PDFs in parallel and return contents
def download_pdfs_parallel(urls):
    results = {}
    with ThreadPoolExecutor(max_workers=8) as executor:  # Adjust number of workers based on CPU capacity
        futures = {executor.submit(download_pdf, url): url for url in urls}

        for future in as_completed(futures):
            url, content = future.result()
            if content:
                results[url] = content  # Store content by URL key
            else:
                logger.warning(f"No content downloaded for {url}")

    return results  # Return dictionary with URLs and their content

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
def get_relevant_chunks(pdf_content, query, chunk_size=1000, top_n=3):
    text = extract_text_from_pdf(pdf_content)
    chunks = chunk_text(text, chunk_size)
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(chunks)
    query_vec = vectorizer.transform([query])
    similarity_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = similarity_scores.argsort()[-top_n:][::-1]
    top_chunks = [(chunks[i], similarity_scores[i]) for i in top_indices]
    return top_chunks

# Worker function for multithreading
def worker(urls, result_list, index):
    for url in urls:
        content = download_pdf(url)
        if content:
            result_list[index].append(content)

# Function to download PDFs using multiple threads
def download_pdfs_from_urls(urls, numberOfWorkers):
    results = [[] for _ in range(numberOfWorkers)]
    chunk_size = len(urls) // numberOfWorkers
    threads = []

    for i in range(numberOfWorkers):
        start_index = i * chunk_size
        end_index = (i + 1) * chunk_size if i != numberOfWorkers - 1 else len(urls)
        thread = threading.Thread(target=worker, args=(urls[start_index:end_index], results, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return [pdf_content for sublist in results for pdf_content in sublist if pdf_content]

# Function to handle the entire process of downloading and generating relevant chunks
def generate_chunks(urls, user_query, numberOfWorkers=3, chunk_size=1000, top_n=3):
    logger.info("Starting PDF download process.")
    pdfs = download_pdfs_from_urls(urls, numberOfWorkers)

    logger.info(f"Downloaded {len(pdfs)} PDFs. Extracting relevant chunks for the query.")
    all_relevant_chunks = []

    for pdf_content in pdfs:
        relevant_chunks = get_relevant_chunks(pdf_content, user_query, chunk_size, top_n)
        all_relevant_chunks.extend(relevant_chunks)

    logger.info("Completed extraction of relevant chunks.")
    return all_relevant_chunks
