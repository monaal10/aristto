import stripe
from flask import Flask, send_from_directory
import logging
import datetime
import uuid

from main.modules.answer_a_question_module import answer_a_question
from main.modules.chat_with_paper_module import chat
from main.modules.extract_paper_info_module import extract_paper_information
from main.modules.literature_review_agent_module import execute_literature_review
from main.utils import string_utils
from main.utils.chunk_operations import parallel_download_and_chunk_papers, get_relevant_chunks
from main.modules.relevant_papers_module import get_relevant_papers
from flask_cors import CORS
from main.classes.mongodb import insert_data, fetch_data, update_data
from main.utils.constants import RESEARCH_PAPER_DATABASE, LITERATURE_REVIEW_DATABASE, RELEVANT_CHUNKS_TO_RETRIEVE, \
    MONGODB_SET_OPERATION, APPLICATION_SECRET_KEY, SAVED_PAPERS_DATABASE, STRIPE_API_KEY, CLIENT_URL, USERS_DATABASE, \
    STRIPE_WEBHOOKS_SECRET_KEY
from main.utils.convert_data import convert_oa_response_to_research_paper, convert_mongodb_to_research_paper
from main.utils.json_encoder import JSONEncoder
from main.utils.string_utils import JsonResp
from flask import Blueprint
from main.utils.mocks import MOCK_RESPONSE_JSON
from main.user.models import User, Plan
from main.utils.auth_utils import token_required
from flask import jsonify, request
from bson.json_util import dumps
import json
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://0.0.0.0:8000",
    "http://localhost:3000",    # Common React development port
    "http://127.0.0.1:3000",
    "http://localhost:5000",    # Common Flask development port
    "http://127.0.0.1:5000",
    "http://localhost:5173",    # Vite default port
    "http://127.0.0.1:5173",
    "http://localhost:8080",    # Another common development port
    "http://127.0.0.1:8080",
    "http://[::1]:8000",       # IPv6 localhost
    "http://[::1]:3000",
    "http://[::1]:5000",
    "http://[::1]:5173",
    "http://[::1]:8080",
    "https://aristto.com"
]

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

@user_blueprint.route("/refresh-token", methods=["POST", 'OPTIONS'])
@token_required
def refresh_token():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    return User().refresh()

@user_blueprint.route("/update-subscription", methods=["POST", 'OPTIONS'])
@token_required
def update_user_subscription():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    return User().update_subscription()

@user_blueprint.route('/reset-password', methods=['POST'])
def request_password_reset():
    return User().request_password_reset()

@user_blueprint.route('/reset-password/confirm', methods=['POST'])
def reset_password():
    return User().reset_password()
application = Flask(__name__, static_folder='main/static', static_url_path='')
application.config["secret_key"] = APPLICATION_SECRET_KEY
# Configure CORS
CORS(application, supports_credentials=True)


# Add CORS headers to all responses
@application.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin in ALLOWED_ORIGINS or (origin and origin.endswith('elasticbeanstalk.com')):
        response.headers.add('Access-Control-Allow-Origin', origin)
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Expose-Headers', 'Set-Cookie')
    return response


application.register_blueprint(user_blueprint, url_prefix="/user")


@application.route('/')
def serve_react():
    return send_from_directory('main/static', 'index.html')

@application.route('/assets/<path:filename>')
def serve_static(filename):
    return send_from_directory('main/static/assets', filename,
                             mimetype='text/css' if filename.endswith('.css') else 'application/javascript')

@application.route('/<path:filename>')
def serve_files(filename):
    return send_from_directory('main/static', filename)

@application.route("/")
def index():
    return JsonResp({"status": "Online"}, 200)

@application.route('/reset-password/<token>')
def reset_password_route(token):
    return send_from_directory(application.static_folder, 'index.html')
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
        papers = []
        for paper_id in paper_ids_dict:
            papers.extend(fetch_data(paper_id, RESEARCH_PAPER_DATABASE))
        final_papers = [convert_mongodb_to_research_paper(paper) for paper in papers]
        relevant_chunks = []
        if len(final_papers) > 1:
            for paper in final_papers:
                if not paper.pdf_content:
                    paper = parallel_download_and_chunk_papers([paper])[0]
                    insert_data(paper.dict(), RESEARCH_PAPER_DATABASE)
                relevant_chunks.extend(get_relevant_chunks(query, [paper])[:5])
        else:
            relevant_chunks = [{"title": final_papers[0].title, "chunk_text": final_papers[0].pdf_content}]
        result = chat(query, relevant_chunks, conversation_history[:-5])
        conversation_history.append({"human_message": query, "assistant_message": result.content})
        response = {"answer": result.content, "conversation_history": conversation_history}
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
        if not query:
            return string_utils.JsonResp({"message": "No query provided"}, 400)
        start_year = data.get('start_year', None)
        end_year = data.get('end_year', None)
        citation_count = data.get('citation_count', None)
        authors = data.get('authors', None)
        published_in = data.get('published_in', None)
        literature_review = execute_literature_review(query, start_year, end_year, citation_count, published_in, authors)
        literature_review_dict = literature_review.dict()
        papers = [reference.reference_metadata.dict() for reference in literature_review.references]
        literature_review_id = uuid.uuid4()
        response = {
            "literatureReviewName": query,
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
    #return jsonify(MOCK_RESPONSE_JSON)

@application.route('/getRelevantPapers', methods=['POST', 'OPTIONS'])
def get_papers():
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
        papers_json = [paper.dict() for paper in relevant_papers]
        insert_data(papers_json, RESEARCH_PAPER_DATABASE)
        return jsonify({"references": papers_json})
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
        response = fetch_data({"userId": user_id}, LITERATURE_REVIEW_DATABASE)
        return json.dumps(response, cls=JSONEncoder), 200, {'Content-Type': 'application/json'}
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


@application.route('/savePapers', methods=['POST', 'OPTIONS'])
def save_papers():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    try:
        data = request.json
        user_id = data.get('user_id', None)
        paper_id = data.get('paper_id', None)
        collection_id = data.get('collection_id', None)
        collection_name = data.get('collection_name', None)
        if not user_id:
            return string_utils.JsonResp({"message": "User not logged in"}, 400)
        if not collection_id:
            collection_id = str(uuid.uuid4())
        insert_data({"userId": user_id, "paperId": paper_id, "collectionId": collection_id,
                     "collectionName": collection_name}, SAVED_PAPERS_DATABASE)
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        raise e


@application.route('/getCollections', methods=['POST', 'OPTIONS'])
def get_collections():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    try:
        data = request.json
        user_id = data.get('user_id', None)
        papers_in_collection = {}

        if not user_id:
            return string_utils.JsonResp({"message": "User not logged in"}, 400)

        collections = fetch_data({"userId": user_id}, SAVED_PAPERS_DATABASE)
        if len(collections) == 0:
            return jsonify([])

        unique_collections = {}
        for entry in collections:
            if entry:
                collection_id = str(entry["collectionId"])  # Convert ObjectId to string
                collection_name = entry["collectionName"]
                paper = fetch_data({"id": entry["paperId"]}, RESEARCH_PAPER_DATABASE)[0]

            # Convert any ObjectId in paper to string
                paper = json.loads(dumps(paper))

                if papers_in_collection.get(collection_id):
                    papers_in_collection[collection_id].append(paper)
                else:
                    papers_in_collection[collection_id] = [paper]

                if collection_id not in unique_collections:
                    unique_collections[collection_id] = collection_name

        filtered_list = [
            {
                "collection_id": k,
                "collection_name": v,
                "papers": papers_in_collection[k]
            }
            for k, v in unique_collections.items()
        ]

        # Use custom JSON encoder to handle any remaining ObjectId instances
        return json.dumps(filtered_list, cls=JSONEncoder), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        print(f"Error in get_collections: {str(e)}")
        return jsonify({"error": str(e)}), 500



@application.route('/stripeWebhooks', methods=['POST'])
def webhook():
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']
    stripe.api_key = STRIPE_API_KEY
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOKS_SECRET_KEY
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    if event['type'] == 'customer.subscription.created':
      subscription = event['data']['object']
      subscription_status = subscription['status']
      if subscription_status == "trialing" or subscription_status == "active":
          customer_id = subscription['customer']
          customer = stripe.Customer.retrieve(customer_id)
          customer_email = customer['email']
          update_fields = {
              "plan": Plan.PRO.value,
              "stripe_customer_id": customer_id
          }
          update_data(
              update_fields,
              USERS_DATABASE,
              {"email": customer_email},
              MONGODB_SET_OPERATION
          )
    elif event['type'] == 'customer.subscription.deleted':
      subscription = event['data']['object']
      stripe_customer_id = subscription['customer']
      update_fields = {
          "plan": Plan.FREE.value
      }
      update_data(
          update_fields,
          USERS_DATABASE,
          {"stripe_customer_id": stripe_customer_id},
          MONGODB_SET_OPERATION
      )

    else:
      print('Unhandled event type {}'.format(event['type']))

    return jsonify(success=True)
@application.route('/', defaults={'path': ''})
@application.route('/<path:path>')
def catch_all(path):
    return send_from_directory(application.static_folder, 'index.html')

if __name__ == '__main__':
    application.run(host="0.0.0.0", port=8000, debug=True)
