import io
import datetime

from paperqa import Docs
import re
import os

from download_pdf import download_pdf

os.environ['OPENAI_API_KEY'] = 'sk-zFNU8L6Nkc1e-2VgAKoSB8tBcuEgJ140flDuDTc0muT3BlbkFJ_ChBKzjg63-HOPaPNczEzxWVoahtCUU9g1ZsZzBvgA'
prompt_for_references = "The paper (OrigamiNet: Weakly-Supervised, Segmentation-Free, One-Step, Full Page Text Recognition by learning to unfold) in this list scites the second one (Scan, Attend and Read: End-to-End Handwritten Paragraph Recognition with MDLSTM Attention). Can you tell me what concepts of the paper that is scited are used in the first paper?"
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
    print(datetime.datetime.now())
    docs = Docs(llm='gpt-4o-mini-2024-07-18', summary_llm="gpt-4o-mini-2024-07-18")
    for doc_url in doc_urls:
        pdf_content = download_pdf(doc_url)
        if pdf_content:
         docs.add_file(io.BytesIO(pdf_content))
    response = docs.query(query)
    print(datetime.datetime.now())
    return response.answer

#print(get_answer_from_paperqa(["https://arxiv.org/pdf/2006.07491","https://arxiv.org/pdf/1909.11573", "https://ijies.net/finial-docs/finial-pdf/010822785.pdf", "https://arxiv.org/pdf/2107.02612", "https://ieeexplore.ieee.org/ielx7/6287639/9668973/09712265.pdf", "https://www.scirp.org/pdf/jcc_2021051813373227.pdf"],
                              #"What are the 3 most important concepts mentioned in this paper? Which reference papers do these concepts come from?"))
                              #"Give me information about the following things of this research paper : 1. What are the major contributions of this paper? 2. What are the limitations of this paper? What dataset is being used in this paper if any? Give me an answer in bullet point format for each question."))
 #                           "Analyze these papers and tell me what the main purpose of each of them is. Also tell me what methodologies have they used?"))