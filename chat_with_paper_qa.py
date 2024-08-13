from paperqa import Docs, SentenceTransformerEmbeddingModel
import re
import datetime
from utils.extract_image_utils import download_pdf, cleanup_pdfs
import os
os.environ['OPENAI_API_KEY'] = 'sk-None-IEWqcLkHft3djH66AroZT3BlbkFJ4cCc3ieleT5ArR1On5rK'

def get_reference_content(reference_names, response):
    reference_content = []
    for reference_name in reference_names:
        for context in response.contexts:
            if reference_name == context.text.name:
                reference_content.append(context.context)


def extract_page_references(text):
    # Regular expression pattern to match text in brackets containing "pages"
    pattern = r'\(([^()]*pages[^()]*)\)'

    # Find all matches in the text
    matches = re.findall(pattern, text)

    return matches


def get_answer_from_paperqa(doc_paths, query):

    doc_paths = doc_paths

    docs = Docs(llm='gpt-4o-mini-2024-07-18')

    for d in doc_paths:
        docs.add(d)

    response = docs.query(query)
    return response.answer


def get_answer(pdf_urls, query):
    doc_paths = [download_pdf(pdf_url) for pdf_url in pdf_urls]
    answer = get_answer_from_paperqa(doc_paths, query)
    cleanup_pdfs()
    return answer


"""pdf_urls = ["https://arxiv.org/pdf/2006.07491"]
query = "How does OrigamiNet work?"
time = datetime.datetime.now()
get_answer(pdf_urls, query)"""