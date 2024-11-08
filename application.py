from flask import Flask, request, jsonify, render_template
import logging
import datetime
import uuid

from modules.answer_a_question_module import answer_a_question
from modules.chat_with_paper_module import chat
from modules.extract_paper_info_module import extract_paper_information
from user.routes import user_blueprint
from utils.chunk_operations import parallel_download_and_chunk_papers, get_relevant_chunks
from modules.literature_review_agent_module import analyze_research_query
from modules.relevant_papers_module import get_relevant_papers
from flask_cors import CORS
from classes.mongodb import insert_data, fetch_data, update_data
from utils.constants import RESEARCH_PAPER_DATABASE, LITERATURE_REVIEW_DATABASE, RELEVANT_CHUNKS_TO_RETRIEVE, \
    MONGODB_SET_OPERATION
from utils.convert_data import convert_oa_response_to_research_paper
from utils.string_utils import JsonResp

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

application = Flask(__name__)
cors_config = {
    "origins": ["http://localhost:3000"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Origin", "accesstoken"],
    "expose_headers": ["Content-Type", "Authorization"],
    "supports_credentials": True,
    "max_age": 3600
}

CORS(application, origins=cors_config["origins"], supports_credentials=True, methods=cors_config["methods"],
     allow_headers=cors_config["allow_headers"], expose_headers=cors_config["expose_headers"])
CORS(user_blueprint, origins=cors_config["origins"], supports_credentials=True, methods=cors_config["methods"],
     allow_headers=cors_config["allow_headers"], expose_headers=cors_config["expose_headers"])
application.register_blueprint(user_blueprint, url_prefix="/api/user")


@application.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


@application.route("/api")
def index():
    return JsonResp({"status": "Online"}, 200)


@application.route('/', methods=['GET'])
def main():
    return render_template("start-basic-search.html")


@application.route('/chatWithPapers', methods=['POST'])
def chat_with_papers():
    try:
        start_time = datetime.datetime.now()
        logger.info(f"Request received at: {start_time}")
        data = request.json
        query = data.get('query', None)
        paper_ids = data.get('paper_ids', None)
        paper_ids_dict = [{"id": paper_id} for paper_id in paper_ids]
        papers = fetch_data(paper_ids_dict, RESEARCH_PAPER_DATABASE)
        final_papers = [convert_oa_response_to_research_paper(paper) for paper in papers]
        if len(final_papers) > 1:
            relevant_chunks = get_relevant_chunks(query, final_papers)[:RELEVANT_CHUNKS_TO_RETRIEVE]
        else:
            relevant_chunks = {"1": final_papers[0].pdf_content}

        result = chat(query, relevant_chunks)
        return jsonify(result.dict())
    except Exception as e:
        raise e


@application.route('/askQuestion', methods=['POST'])
def ask_question():
    try:
        start_time = datetime.datetime.now()
        logger.info(f"Request received at: {start_time}")
        data = request.json
        query = data.get('query', None)
        start_year = data.get('start_year', None)
        end_year = data.get('end_year', None)
        citation_count = data.get('citation_count', None)
        authors = data.get('authors', None)
        published_in = data.get('published_in', None)
        relevant_papers = get_relevant_papers(query, start_year, end_year, citation_count, published_in, authors)
        papers_with_chunks = parallel_download_and_chunk_papers(relevant_papers[:10])
        relevant_chunks = get_relevant_chunks(query, papers_with_chunks)[:RELEVANT_CHUNKS_TO_RETRIEVE]
        result = answer_a_question(query, relevant_chunks, papers_with_chunks)
        json_papers = []
        for paper in relevant_papers:
            json_papers.append(vars(paper))
        insert_data(json_papers, RESEARCH_PAPER_DATABASE)
        return jsonify(result.dict())
    except Exception as e:
        raise e


@application.route('/getLiteratureReview', methods=['POST'])
def get_literature_review():
    try:
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
        literature_review = analyze_research_query(query, start_year, end_year, citation_count, published_in, authors)
        literature_review_id = uuid.uuid4()
        response = {
            "userId": user_id,
            "literatureReviewId": literature_review_id,
            "literatureReview": literature_review.dict()
        }
        insert_data(response, LITERATURE_REVIEW_DATABASE)
        return jsonify(response)
    except Exception as e:
        raise e


@application.route('/getPaperInfo', methods=['POST'])
def get_paper_info():
    try:
        start_time = datetime.datetime.now()
        logger.info(f"Request received at: {start_time}")
        data = request.json
        paper_id = data.get('paper_id', None)
        paper = fetch_data({"id": paper_id}, RESEARCH_PAPER_DATABASE)
        final_paper = convert_oa_response_to_research_paper(paper)
        output = extract_paper_information(final_paper.pdf_content)
        for key in output.keys():
            setattr(paper, key, output[key])
        db_filter = {"open_alex_id": paper["open_alex_id"]}
        update_data(paper.dict(), RESEARCH_PAPER_DATABASE, db_filter, MONGODB_SET_OPERATION)
        return jsonify(output.dict())
    except Exception as e:
        raise e


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8000, debug=True)
