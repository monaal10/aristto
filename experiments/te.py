import os
import time
import psutil
import requests
import pymupdf
import concurrent.futures
from functools import partial
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_anthropic import ChatAnthropic

max_workers = 3
max_papers = 3
pdf_dir = "pdfs"
if not os.path.exists(pdf_dir):
    os.makedirs(pdf_dir)

def log_memory_and_time(start_time, step_name):
    end_time = time.time()
    memory_used = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    print(f"{step_name} - Time taken: {end_time - start_time:.2f} seconds, Memory used: {memory_used:.2f} MB")
os.environ['ANTHROPIC_API_KEY'] = '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'
# Initialize Anthropic LLM

llm = ChatAnthropic(model='claude-3-5-sonnet-20240620')

# Initialize embeddings
embeddings = HuggingFaceEmbeddings()

# Theme Identifying Agent
theme_prompt = PromptTemplate(
    input_variables=["query"],
    template="I am a PhD student and have deep knowledge of the domain. Here is the topic that I need to perform a comprehensive literature review on. Query: {query} Give me sub themes/related themes that I should have knowledge about to understand the topic in the query. Your response should be in a format that is a comma-separated list of queries that can be used to find relevant research papers for that query. Limit the number of queries to seven."
)
theme_chain = LLMChain(llm=llm, prompt=theme_prompt)

# Information Extraction Agent
section_prompt = PromptTemplate(
    input_variables=["content", "title"],
    template="""
    I have a research paper titled '{title}'. Please extract and summarize the following sections: Methodology, Approach, and Limitations. For each section, provide the summary and include the page and line numbers where the information was found. Here's the content of the paper:

    {content}

    Format your response as follows:
    Methodology:
    [Summary]
    [Page and line numbers]

    Approach:
    [Summary]
    [Page and line numbers]

    Limitations:
    [Summary]
    [Page and line numbers]
    """
)
extraction_chain = LLMChain(llm=llm, prompt=section_prompt)

def extract_pdf_text(pdf_file_path):
    """Extracts and returns the text content from a PDF file."""
    start_time = time.time()
    print(f"Extracting text from: {pdf_file_path}")
    full_text = ''
    try:
        pdf_document = pymupdf.open(pdf_file_path)
        for page_num, page in enumerate(pdf_document, 1):
            text = page.get_text()
            full_text += f"Page {page_num}:\n{text}\n\n"
        log_memory_and_time(start_time, "Extract PDF Text")
        return full_text
    except Exception as e:
        print(f"Failed to extract text from {pdf_file_path}: {e}")
        return None

def extract_key_sections(paper):
    start_time = time.time()
    print(f"Extracting key sections from paper: {paper['title']}")

    result = extraction_chain.run(content=paper["content"], title=paper["title"])

    log_memory_and_time(start_time, "Extract Key Sections")
    return result

def find_and_extract_papers(user_query, max_papers_per_theme=3):
    start_time = time.time()
    print(f"Finding and extracting papers for the query: {user_query}")

    themes_result = theme_chain.run(user_query)
    themes = [theme.strip() for theme in themes_result.split(',')]
    print(f"Identified themes: {themes}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        all_papers = list(executor.map(partial(find_relevant_papers, max_papers=max_papers_per_theme), themes))

    all_papers = [paper for theme_papers in all_papers for paper in theme_papers]

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        extracted_infos = list(executor.map(extract_key_sections, all_papers))

    for paper, extracted_info in zip(all_papers, extracted_infos):
        paper["extracted_info"] = extracted_info

    log_memory_and_time(start_time, "Find and Extract Papers")
    return all_papers

def find_relevant_papers(theme, max_papers):
    start_time = time.time()
    print(f"Finding relevant papers for theme: {theme}")
    base_url = "https://api.openalex.org/works"
    params = {
        "mailto": "monaalsanghvi1998@gmail.com",
        "search": theme,
        "per_page": max_papers
    }

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}")

    data = response.json()
    papers = []

    with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
        futures = []
        for paper_data in data.get("results", []):
            title = paper_data.get("title")
            pdf_url = paper_data.get('primary_location', {}).get('pdf_url', None)

            if pdf_url:
                futures.append(executor.submit(process_paper, title, pdf_url, theme))

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                papers.append(result)

            if len(papers) >= max_papers:
                break

    log_memory_and_time(start_time, "Find Relevant Papers")
    return papers

def process_paper(title, pdf_url, theme):
    try:
        pdf_name = f"{title.replace(' ', '_')}.pdf"
        print(f"Downloading PDF: {pdf_name} from {pdf_url}")
        pdf_file_path = download_pdf(pdf_url, pdf_name)
        text_content = extract_pdf_text(pdf_file_path)
        return {"title": title, "content": text_content, "theme": theme}
    except Exception as e:
        print(f"Error processing paper '{title}': {str(e)}")
        return None

def download_pdf(pdf_url, pdf_name):
    """Downloads the PDF from the provided URL and saves it in the pdf_dir."""
    start_time = time.time()
    print(f"Downloading PDF: {pdf_name}")
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.44/72.124 Safari/537.36'
    headers = {
        'User-Agent': user_agent
    }
    try:
        response = requests.get(pdf_url, stream=True, headers=headers)
        response.raise_for_status()

        pdf_path = os.path.join(pdf_dir, pdf_name)
        with open(pdf_path, 'wb') as pdf_file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    pdf_file.write(chunk)

        log_memory_and_time(start_time, f"Download PDF: {pdf_name}")
        return pdf_path
    except requests.exceptions.RequestException as e:
        print(f"Failed to download PDF from {pdf_url}: {e}")
        return None

def summarize_sections(papers):
    start_time = time.time()
    print("Generating summaries for all sections...")

    sections = ["Methodology", "Approach", "Limitations"]
    summary_prompt = PromptTemplate(
        input_variables=["section", "content"],
        template="""
        I have extracted information about the {section} from multiple research papers. Please provide a comprehensive summary of the {section} across all papers, citing the specific paper titles and line numbers for each piece of information used in the summary. Here's the extracted information:

        {content}

        Your summary should synthesize the information from all papers, highlighting common themes, unique approaches, and significant findings. Make sure to cite the specific papers and line numbers for each piece of information used in the summary.
        """
    )
    summary_chain = LLMChain(llm=llm, prompt=summary_prompt)

    def summarize_section(section):
        section_content = "\n\n".join([f"Paper: {paper['title']}\n{paper['extracted_info']}" for paper in papers])
        return summary_chain.run(section=section, content=section_content)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        summaries = {section: executor.submit(summarize_section, section) for section in sections}

    summaries = {section: future.result() for section, future in summaries.items()}

    log_memory_and_time(start_time, "Summarize Sections")
    return summaries

def create_vector_store(papers):
    start_time = time.time()
    print("Creating vector store...")

    documents = []
    for paper in papers:
        doc = Document(
            page_content=paper["extracted_info"],
            metadata={"title": paper["title"], "theme": paper["theme"]}
        )
        documents.append(doc)

    vector_store = FAISS.from_documents(documents, embeddings)

    log_memory_and_time(start_time, "Create Vector Store")
    return vector_store

# Example usage
user_query = "What are the latest developments in renewable energy and their impact on climate change?"
processed_papers = find_and_extract_papers(user_query)
summaries = summarize_sections(processed_papers)
vector_store = create_vector_store(processed_papers)

# Print results
for paper in processed_papers:
    print(f"Theme: {paper['theme']}, Title: {paper['title']}")
    print("Extracted Information:")
    print(paper["extracted_info"])
    print("="*50)

print("Summaries:")
for section, summary in summaries.items():
    print(f"\n{section}:")
    print(summary)
    print("="*50)

# Perform similarity search
search_query = "What are the proposed solutions for renewable energy?"
print(f"Performing similarity search for query: '{search_query}'")
similar_docs = vector_store.similarity_search(search_query, k=3)

print("Similar documents:")
for doc in similar_docs:
    print(f"Title: {doc.metadata['title']}")
    print(f"Theme: {doc.metadata['theme']}")
    print(f"Content: {doc.page_content[:200]}...")  # Print first 200 characters
    print("="*50)