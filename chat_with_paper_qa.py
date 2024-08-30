import io

from paperqa import Docs
import re
import os

from extract_figures import download_pdf

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

def get_answer_from_paperqa(doc_urls, query):
    """current_path = os.getcwd()
    file_paths = []
    for i in doc_urls:
        pdf_name = f"downloaded_{i+1}.pdf"
        response = download_pdf(i)
    # Construct the full path for the PDF file
        file_path = os.path.join(current_path, pdf_name)
    # Write the content to a file
        with open(file_path, 'wb') as f:
            f.write(response.content)
        file_paths.append(file_path)"""
    docs = Docs(llm='gpt-4o-mini-2024-07-18', summary_llm="gpt-4o-mini-2024-07-18")
    for doc_url in doc_urls:
        docs.add_file(io.BytesIO(download_pdf(doc_url)))
    response = docs.query(query)
    return response.answer

