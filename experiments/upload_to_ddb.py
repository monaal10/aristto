from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import requests
import pymupdf
import os
import getpass
import time
import psutil
import networkx as nx
from collections import Counter
import itertools

pdf_dir = "pdfs"
if not os.path.exists(pdf_dir):
    os.makedirs(pdf_dir)

def log_memory_and_time(start_time, step_name):
    end_time = time.time()
    memory_used = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    print(f"{step_name} - Time taken: {end_time - start_time:.2f} seconds, Memory used: {memory_used:.2f} MB")

os.environ['OPENAI_API_KEY'] = 'sk-zFNU8L6Nkc1e-2VgAKoSB8tBcuEgJ140flDuDTc0muT3BlbkFJ_ChBKzjg63-HOPaPNczEzxWVoahtCUU9g1ZsZzBvgA'
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")
# Initialize OpenAI LLM
llm = OpenAI(temperature=0.7)

# Theme Identifying Agent
theme_prompt = PromptTemplate(
    input_variables=["query"],
    template="Identify the main themes in this query. Return them as a comma-separated list: {query}"
)
theme_chain = LLMChain(llm=llm, prompt=theme_prompt)

# Information Extraction Agent
section_prompt = PromptTemplate(
    input_variables=["chunk", "section"],
    template="""
        Extract the following {section} from the provided text:
        Text:
        {chunk}
    """
)


# LLM Chains
extraction_chain = LLMChain(llm=llm, prompt=section_prompt)

# Text splitter for chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=200,
    length_function=len
)

def extract_pdf_text(pdf_file_path):
    """Extracts and returns the text content from a PDF file."""
    start_time = time.time()
    print(f"Extracting text from: {pdf_file_path}")
    full_text = ''
    try:
        # Open the PDF file
        pdf_document = pymupdf.open(pdf_file_path)
        for page in pdf_document:
            full_text += page.get_text()
        log_memory_and_time(start_time, "Extract PDF Text")
        return full_text
    except Exception as e:
        print(f"Failed to extract text from {pdf_file_path}: {e}")
        return None

def extract_key_sections(paper_content):
    start_time = time.time()
    print("Extracting key sections from paper...")
    chunks = text_splitter.split_text(paper_content)
    methodology_info = []
    proposed_info = []
    limitations_info = []

    for chunk in chunks:
        methodology_info.append(extraction_chain.run({"chunk": chunk, "section": "Methodology"}))
        proposed_info.append(extraction_chain.run({"chunk": chunk, "section": "Proposed Solution"}))
        limitations_info.append(extraction_chain.run({"chunk": chunk, "section": "Limitation"}))
    result = {
        "methodology": " ".join(methodology_info),
        "proposed": " ".join(proposed_info),
        "limitations": " ".join(limitations_info),
    }
    log_memory_and_time(start_time, "Extract Key Sections")
    return result

def find_and_extract_papers(user_query, max_papers_per_theme=3):
    start_time = time.time()
    print(f"Finding and extracting papers for the query: {user_query}")
    themes_result = theme_chain.run(user_query)
    themes = [theme.strip() for theme in themes_result.split(',')]
    print(f"Identified themes: {themes}")

    all_papers = []
    for theme in themes:
        theme_papers = find_relevant_papers(theme, max_papers_per_theme)
        for paper in theme_papers:
            extracted_info = extract_key_sections(paper["content"])
            paper["extracted_info"] = extracted_info
            all_papers.append(paper)

    log_memory_and_time(start_time, "Find and Extract Papers")
    return all_papers

def process_paper_in_chunks(paper_content):
    start_time = time.time()
    print("Processing paper in chunks...")
    chunks = text_splitter.split_text(paper_content)
    extracted_infos = []

    for chunk in chunks:
        extracted_info = extract_chain.run(chunk)
        extracted_infos.append(extracted_info)

    combined_info = " ".join(extracted_infos)

    if len(combined_info) > 2000:
        summary_prompt = PromptTemplate(
            input_variables=["text"],
            template="Summarize the key points from this text in no more than 500 words: {text}"
        )
        summary_chain = LLMChain(llm=llm, prompt=summary_prompt)
        combined_info = summary_chain.run(combined_info)

    log_memory_and_time(start_time, "Process Paper in Chunks")
    return combined_info

def find_relevant_papers(theme, max_papers=3):
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

    for paper_data in data.get("results", []):
        title = paper_data.get("title")
        pdf_url = paper_data.get('primary_location', {}).get('pdf_url', None)

        if pdf_url:
            try:
                pdf_name = f"{title.replace(' ', '_')}.pdf"
                print(f"Downloading PDF: {pdf_name} from {pdf_url}")
                pdf_file_path = download_pdf(pdf_url, pdf_name)
                text_content = extract_pdf_text(pdf_file_path)
                papers.append({"title": title, "content": text_content, "theme": theme})
            except Exception as e:
                print(f"Error processing paper '{title}': {str(e)}")
                continue
        else:
            print(f"No PDF URL found for paper: {title}")
            continue

        if len(papers) >= max_papers:
            break

    log_memory_and_time(start_time, "Find Relevant Papers")
    return papers

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

# Create a graph from extracted terms and their relationships
def create_term_graph(paper_data):
    G = nx.Graph()

    # Iterate over each paper and its sections
    for paper in paper_data:
        for section, content in paper["extracted_info"].items():
            key_terms = extract_key_terms(content)

            # Add nodes and edges to the graph
            for term1, term2 in itertools.combinations(key_terms, 2):
                if G.has_edge(term1, term2):
                    G[term1][term2]['weight'] += 1
                else:
                    G.add_edge(term1, term2, weight=1)

    # Normalize edge weights
    for u, v, d in G.edges(data=True):
        d['weight'] /= len(paper_data)  # Normalization based on number of papers

    return G

def extract_key_terms(content):
    # Split the content into smaller chunks
    chunks = text_splitter.split_text(content)

    all_key_terms = set()  # Use a set to avoid duplicate key terms

    for chunk in chunks:
        # Extract key terms from each chunk using the LLM
        theme_result = theme_chain.run({"query": chunk})

        # Split the result and add the terms to the set
        key_terms = [term.strip() for term in theme_result.split(',')]
        all_key_terms.update(key_terms)  # Add terms to the set to avoid duplicates

    return list(all_key_terms)  # Convert set back to list for final result


# Summarize sections based on graph
def summarize_sections(G, section_name):
    start_time = time.time()
    print(f"Generating summary for {section_name}...")

    # Find the most connected nodes in the graph (e.g., terms with the highest degree)
    most_connected_nodes = sorted(G.degree, key=lambda x: x[1], reverse=True)

    # Generate a summary based on the top terms
    top_terms = [node for node, _ in most_connected_nodes[:10]]  # Top 10 terms

    summary = f"The {section_name} involves key themes such as: {', '.join(top_terms)}."

    log_memory_and_time(start_time, f"Summarize {section_name}")
    return summary

# Add these summaries to each section of the paper
def add_summaries_to_papers(papers, G):
    for paper in papers:
        for section in ["methodology", "proposed", "limitations"]:
            paper["summary_" + section] = summarize_sections(G, section)
    return papers

# Updated vector store creation with graph-based insights
def create_vector_store_with_graph(papers):
    start_time = time.time()
    print("Creating vector store with graph insights...")

    G = create_term_graph(papers)
    papers_with_summaries = add_summaries_to_papers(papers, G)

    documents = []
    for paper in papers_with_summaries:
        documents.append(Document(
            page_content=paper["summary_methodology"],
            metadata={"type": "methodology", "title": paper["title"], "theme": paper["theme"]}
        ))
        documents.append(Document(
            page_content=paper["summary_proposed"],
            metadata={"type": "proposed", "title": paper["title"], "theme": paper["theme"]}
        ))
        documents.append(Document(
            page_content=paper["summary_limitations"],
            metadata={"type": "limitations", "title": paper["title"], "theme": paper["theme"]}
        ))

    # Vector store creation
    vector_store = InMemoryVectorStore.from_documents(documents, OpenAIEmbeddings())

    log_memory_and_time(start_time, "Create Vector Store with Graph Insights")
    return vector_store

# Example usage
user_query = "What are the latest developments in renewable energy and their impact on climate change?"
processed_papers = find_and_extract_papers(user_query)
vector_store_with_graph = create_vector_store_with_graph(processed_papers)

# Perform similarity search
search_query = "What are the proposed solutions for renewable energy?"
print(f"Performing similarity search for query: '{search_query}'")
docs = vector_store_with_graph.similarity_search(search_query, k=5)

# Print results
for paper in processed_papers:
    print(f"Theme: {paper['theme']}, Title: {paper['title']}")
    print("Extracted Information:")
    print(paper["extracted_info"])
    print("="*50)

print(f"Similarity search results for query '{search_query}':")
for doc in docs:
    print(doc)