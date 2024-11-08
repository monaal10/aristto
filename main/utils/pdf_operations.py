import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import io
import requests
import PyPDF2

from utils.constants import RESEARCH_PAPER_DATABASE
from classes.mongodb import fetch_data
from classes.research_paper import ResearchPaper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Function to download a single PDF from a URL
def download_pdf(paper):
    result = fetch_data(paper, RESEARCH_PAPER_DATABASE)
    if len(result) == 1 and result["pdf_content"]:
        return ResearchPaper(result)
    url = paper.oa_url
    try:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.44/72.124 Safari/537.36'
        headers = {
            'User-Agent': user_agent
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes

        logger.info(f"Downloaded {url} successfully.")
        text = extract_text_from_pdf(response.content)
        paper.pdf_content = text
        return paper  # Return URL and its content
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        paper.pdf_content = None
        return paper  # Return None if there's an error


# Function to download PDFs in parallel and return contents
def download_pdfs_parallel(papers):
    final_papers = []
    with ThreadPoolExecutor(max_workers=8) as executor:  # Adjust number of workers based on CPU capacity
        futures = {executor.submit(download_pdf, paper): paper for paper in papers}

        for future in as_completed(futures):
            paper = future.result()
            if paper.pdf_content:
                final_papers.append(paper)

    return final_papers  # Return dictionary with URLs and their content


def extract_text_from_pdf(pdf_content):
    try:
        text = ""
        pdf_stream = io.BytesIO(pdf_content)
        reader = PyPDF2.PdfReader(pdf_stream)
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        raise f"Failed to extract text from PDF: {e}"
