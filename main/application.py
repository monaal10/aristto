from flask import Flask, request, jsonify
import logging
import datetime
import uuid

from modules.answer_a_question_module import answer_a_question
from modules.chat_with_paper_module import chat
from modules.extract_paper_info_module import extract_paper_information
from utils import string_utils
from utils.chunk_operations import parallel_download_and_chunk_papers, get_relevant_chunks
from modules.literature_review_agent_module import execute_literature_review
from modules.relevant_papers_module import get_relevant_papers
from flask_cors import CORS
from classes.mongodb import insert_data, fetch_data, update_data
from utils.constants import RESEARCH_PAPER_DATABASE, LITERATURE_REVIEW_DATABASE, RELEVANT_CHUNKS_TO_RETRIEVE, \
    MONGODB_SET_OPERATION, APPLICATION_SECRET_KEY, SAVED_PAPERS_DATABASE
from utils.convert_data import convert_oa_response_to_research_paper, convert_mongodb_to_research_paper
from utils.string_utils import JsonResp
from flask import Blueprint
from utils.mocks import MOCK_RESPONSE_JSON, ASK_QUESTION_MOCK_RESPONSE
from user.models import User
from utils.auth_utils import token_required

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

user_blueprint = Blueprint("user", __name__)


@user_blueprint.route("/profile", methods=["GET", 'OPTIONS'])
@token_required
def get():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    return User().get()


@user_blueprint.route("/auth", methods=["GET", 'OPTIONS'])
@token_required
def getAuth():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    return User().getAuth()


@user_blueprint.route("/login", methods=["POST", 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    return User().login()


@user_blueprint.route("/logout", methods=["GET", 'OPTIONS'])
@token_required
def logout():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    return User().logout()


@user_blueprint.route("/create", methods=["POST", 'OPTIONS'])
def add():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    return User().add()


application = Flask(__name__)
application.config["secret_key"] = APPLICATION_SECRET_KEY
# Configure CORS
CORS(application)


# Add CORS headers to all responses
@application.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,Access-Control-Allow-Origin, accesstoken')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


application.register_blueprint(user_blueprint, url_prefix="/user")


@application.route("/")
def index():
    return JsonResp({"status": "Online"}, 200)


@application.route('/chatWithPapers', methods=['POST', 'OPTIONS'])
def chat_with_papers():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    try:
        start_time = datetime.datetime.now()
        logger.info(f"Request received at: {start_time}")
        data = request.json
        query = data.get('query', None)
        paper_ids = data.get('paper_ids', None)
        conversation_history = data.get('conversation_history', [])
        paper_ids_dict = [{"id": paper_id} for paper_id in paper_ids]
        papers = fetch_data(paper_ids_dict, RESEARCH_PAPER_DATABASE)
        final_papers = [convert_oa_response_to_research_paper(paper) for paper in papers]
        if len(final_papers) > 1:
            relevant_chunks = get_relevant_chunks(query, final_papers)[:RELEVANT_CHUNKS_TO_RETRIEVE]
        else:
            relevant_chunks = {"1": final_papers[0].pdf_content}
        result = chat(query, relevant_chunks, conversation_history[:-5])
        conversation_history.append({"human_message": query, "Assistant message": result})
        response = {"answer": result, "conversation_history": conversation_history}
        return jsonify(response)
    except Exception as e:
        raise e


@application.route('/askQuestion', methods=['POST', 'OPTIONS'])
def ask_question():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    try:
        start_time = datetime.datetime.now()
        logger.info(f"Request received at: {start_time}")
        data = request.json
        query = data.get('query', None)
        if not query or len(query) == 0:
            return string_utils.JsonResp({"message": "No query provided"}, 400)
        start_year = data.get('start_year', None)
        end_year = data.get('end_year', None)
        citation_count = data.get('citation_count', None)
        authors = data.get('authors', None)
        published_in = data.get('published_in', None)
        relevant_papers = get_relevant_papers(query, start_year, end_year, citation_count, published_in, authors)
        papers_with_chunks = parallel_download_and_chunk_papers(relevant_papers[:10])
        relevant_chunks = get_relevant_chunks(query, papers_with_chunks)[:RELEVANT_CHUNKS_TO_RETRIEVE]
        result = answer_a_question(query, relevant_chunks, papers_with_chunks)
        papers_json = [paper.dict() for paper in papers_with_chunks]
        insert_data(papers_json, RESEARCH_PAPER_DATABASE)
        return jsonify(result.dict())
    except Exception as e:
        raise e


@application.route('/getLiteratureReview', methods=['POST', 'OPTIONS'])
def get_literature_review():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    try:
        start_time = datetime.datetime.now()
        logger.info(f"Request received at: {start_time}")
        data = request.json

        user_id = data.get('user_id', None)
        query = data.get('query', None)
        if not query or len(query) == 0:
            return string_utils.JsonResp({"message": "No query provided"}, 400)
        start_year = data.get('start_year', None)
        end_year = data.get('end_year', None)
        citation_count = data.get('citation_count', None)
        authors = data.get('authors', None)
        published_in = data.get('published_in', None)
        literature_review = execute_literature_review(query, start_year, end_year, citation_count, published_in, authors)
        literature_review_dict = literature_review.dict()
        papers = [reference.dict() for reference in literature_review.references]
        literature_review_id = uuid.uuid4()
        response = {
            "userId": user_id,
            "literatureReviewId": str(literature_review_id),
            "literatureReview": literature_review_dict
        }
        insert_data(response, LITERATURE_REVIEW_DATABASE)
        insert_data(papers, RESEARCH_PAPER_DATABASE)
        if response.get("_id"):
            response["_id"] = str(response.get("_id"))
        return jsonify(response)
    except Exception as e:
        raise e



@application.route('/getPaperInfo', methods=['POST', 'OPTIONS'])
def get_paper_info():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    try:
        start_time = datetime.datetime.now()
        logger.info(f"Request received at: {start_time}")
        data = request.json
        paper_id = data.get('paper_id', None)
        paper = fetch_data({"open_alex_id": paper_id}, RESEARCH_PAPER_DATABASE)[0]
        final_paper = convert_mongodb_to_research_paper(paper)
        output = extract_paper_information(final_paper.pdf_content)
        paper["extracted_info"] = {}
        for key in output.model_fields.keys():
            paper["extracted_info"][key] = getattr(output, key)
        db_filter = {"open_alex_id": paper["open_alex_id"]}
        update_data(paper, RESEARCH_PAPER_DATABASE, db_filter, MONGODB_SET_OPERATION)
        return jsonify(output.dict())
    except Exception as e:
        raise e

@application.route('/getSavedLiteratureReviews', methods=['POST', 'OPTIONS'])
def get_saved_literature_reviews():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    try:
        data = request.json
        user_id = data.get('user_id', None)
        if not user_id:
            return string_utils.JsonResp({"message": "User not logged in"}, 400)
        return jsonify(fetch_data({"userId": user_id}, LITERATURE_REVIEW_DATABASE)[0])
    except Exception as e:
        raise e


@application.route('/getSavedPapers', methods=['POST', 'OPTIONS'])
def get_saved_papers():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    try:
        data = request.json
        user_id = data.get('user_id', None)
        if not user_id:
            return string_utils.JsonResp({"message": "User not logged in"}, 400)
        mongodb_data = fetch_data({"userId": user_id}, SAVED_PAPERS_DATABASE)
        paper_ids = []
        papers = []
        for paper in mongodb_data:
            paper_ids.append(paper["paperId"])
        for paper_id in paper_ids:
            papers.append(fetch_data({"id": paper_id}, SAVED_PAPERS_DATABASE)[0])
        return jsonify(papers)
    except Exception as e:
        raise e


@application.route('/savePaper', methods=['POST', 'OPTIONS'])
def save_paper():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    try:
        data = request.json
        user_id = data.get('user_id', None)
        paper_id = data.get('paper_id', None)
        if not user_id:
            return string_utils.JsonResp({"message": "User not logged in"}, 400)
        insert_data({"userId": user_id, "paperId": paper_id}, SAVED_PAPERS_DATABASE)
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        raise e




if __name__ == '__main__':
    application.run(debug=True)
