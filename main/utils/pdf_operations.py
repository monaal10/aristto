import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import io
import requests
import pypdf

from main.utils.constants import RESEARCH_PAPER_DATABASE
from main.classes.mongodb import fetch_data
from main.utils.convert_data import convert_mongodb_to_research_paper
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Function to download a single PDF from a URL
def download_pdf(paper):
    result = fetch_data({"open_alex_id": paper.open_alex_id}, RESEARCH_PAPER_DATABASE)
    if len(result) == 1 and result[0].get("pdf_content"):
        logger.info(f"Retrieved paper with id : {paper.open_alex_id} from database")
        return convert_mongodb_to_research_paper(result[0])
    url = paper.oa_url
    if paper.isPdfUrl and paper.oa_url and len(paper.oa_url) > 0:
        try:
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Safari/537.36'
            headers = {
                'User-Agent': user_agent
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for bad status codes
            text = extract_text_from_pdf(response.content)
            paper.pdf_content = text
            logger.info(f"Downloaded {url} successfully.")
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
    return paper


# Function to download PDFs in parallel and return contents
def download_pdfs_parallel(papers):
    final_papers = []
    with ThreadPoolExecutor(max_workers=8) as executor:  # Adjust number of workers based on CPU capacity
        futures = {executor.submit(download_pdf, paper): paper for paper in papers}

        for future in as_completed(futures):
            paper = future.result()
            if paper.pdf_content:
                final_papers.append(paper)
            else:
                if paper.abstract and len(paper.abstract) > 0:
                    paper.pdf_content = paper.abstract
                    final_papers.append(paper)
    return final_papers  # Return dictionary with URLs and their content


def extract_text_from_pdf(pdf_content):
    try:
        text = ""
        pdf_stream = io.BytesIO(pdf_content)
        reader = pypdf.PdfReader(pdf_stream)
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {e}")
