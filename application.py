from flask import Flask, request, jsonify, render_template
import logging
import datetime
import uuid

from modules.answer_a_question_module import answer_a_question
from modules.chat_with_paper_module import chat
from modules.extract_paper_info_module import extract_paper_information
from utils.chunk_operations import parallel_download_and_chunk_papers, get_relevant_chunks
from modules.literature_review_agent_module import analyze_research_query
from modules.relevant_papers_module import get_relevant_papers
from flask_cors import CORS
import os
from sentence_transformers import SentenceTransformer
from classes.mongodb import insert_data, fetch_data, update_data

os.environ['OPENAI_API_KEY'] = 'sk-zFNU8L6Nkc1e-2VgAKoSB8tBcuEgJ140flDuDTc0muT3BlbkFJ_ChBKzjg63-HOPaPNczEzxWVoahtCUU9g1ZsZzBvgA'
os.environ['ANTHROPIC_API_KEY'] = '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'
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIA6ODU27KHMGRMPHOZ'
os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
os.environ['SEMANTIC_SCHOLAR_API_KEY'] = 'vd5G9VoPYk3hfCYyPjZR334dvZCumbEF2tkdeQhK'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

application = Flask(__name__)
CORS(application)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
RESEARCH_PAPER_DATABASE = "researchPapers"
@application.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


@application.route('/', methods=['GET'])
def main():
    return render_template("start-basic-search.html")


@application.route('/chatWithPapers', methods=['POST'])
def chat_with_papers():
    start_time = datetime.datetime.now()
    logger.info(f"Request received at: {start_time}")
    data = request.json
    query = data.get('query', None)
    paper_ids = data.get('paper_ids', None)
    paper_ids_dict = [{"id": paper_id} for paper_id in paper_ids]
    papers = fetch_data(paper_ids_dict, RESEARCH_PAPER_DATABASE)
    if len(papers) > 1:
        relevant_chunks = get_relevant_chunks(query, papers)[:5]
    else:
        relevant_chunks = {"1": papers[0].pdf_content}

    result = chat(query, relevant_chunks)
    response = {"answer": result}
    return jsonify(response)


@application.route('/askQuestion', methods=['POST'])
def ask_question():
    top_k = 7
    start_time = datetime.datetime.now()
    logger.info(f"Request received at: {start_time}")
    data = request.json
    user_id = data.get('user_id', None)
    query = data.get('query', None)
    start_year = data.get('start_year', None)
    end_year = data.get('end_year', None)
    citation_count = data.get('citation_count', None)
    authors = data.get('authors', None)
    published_in = data.get('published_in', None)
    relevant_papers = get_relevant_papers(query, start_year, end_year, citation_count, published_in, authors, model)
    papers_with_chunks = parallel_download_and_chunk_papers(relevant_papers)
    relevant_chunks = get_relevant_chunks(query, papers_with_chunks)[:top_k]
    result = answer_a_question(query, relevant_chunks, papers_with_chunks)
    papers = result.get('papers', None)
    json_strings = []
    for paper in papers:
        json_strings.append(vars(paper))
    return vars(result)


@application.route('/getLiteratureReview', methods=['POST'])
def get_literature_review():
    start_time = datetime.datetime.now()
    logger.info(f"Request received at: {start_time}")
    data = request.json
    user_id = data.get('user_id', None)
    query = data.get('query', None)
    start_year = data.get('start_year', None)
    end_year = data.get('end_year', None)
    citation_count = data.get('citation_count', None)
    authors = data.get('authors', None)
    published_in = data.get('published_in', None)
    results = analyze_research_query(query, start_year, end_year, citation_count, published_in, authors)
    literature_review = results.literature_review
    json_strings = []
    for theme_literature_review in literature_review:
        json_strings.append(vars(theme_literature_review))
    literature_review_id = uuid.uuid4()
    response = {
        "userId": user_id,
        "literatureReviewId": literature_review_id,
        "literatureReview": json_strings
    }
    insert_data(json_strings, "LiteratureReviews")
    return jsonify(response)


@application.route('/getPaperInfo', methods=['POST'])
def get_paper_info():
    start_time = datetime.datetime.now()
    logger.info(f"Request received at: {start_time}")
    data = request.json
    paper_id = data.get('paper_id', None)
    paper = fetch_data({"id": paper_id}, RESEARCH_PAPER_DATABASE)
    output = extract_paper_information(paper.pdf_content)
    for key in output.keys():
        setattr(paper, key, output[key])
    update_data(paper, RESEARCH_PAPER_DATABASE)
    return jsonify(output)



if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8000, debug=True)

