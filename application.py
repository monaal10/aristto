import json

from flask import Flask, request, jsonify, render_template
import logging
import datetime
from concurrent.futures import ThreadPoolExecutor

from main.chat_with_paper_qa import get_answer_from_paperqa
from main.get_referenced_papers import fetch_referenced_papers
from main.get_relevant_papers import get_relevant_papers
from flask_cors import CORS
import os
from sentence_transformers import SentenceTransformer
from classes.mongodb import insert_data


os.environ['OPENAI_API_KEY'] = 'sk-zFNU8L6Nkc1e-2VgAKoSB8tBcuEgJ140flDuDTc0muT3BlbkFJ_ChBKzjg63-HOPaPNczEzxWVoahtCUU9g1ZsZzBvgA'
os.environ['ANTHROPIC_API_KEY'] = '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'
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIA6ODU27KHMGRMPHOZ'
os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
os.environ['SEMANTIC_SCHOLAR_API_KEY'] = 'vd5G9VoPYk3hfCYyPjZR334dvZCumbEF2tkdeQhK'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# mongodbClient = MongoDB()
application = Flask(__name__)
CORS(application)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

@application.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


@application.route('/', methods=['GET'])
def main():
    return render_template("start-basic-search.html")


@application.route('/search', methods=['POST'])
def search():
    start_time = datetime.datetime.now()
    logger.info(f"Request received at: {start_time}")
    data = request.json
    query = data.get('query', None)
    start_year = data.get('start_year', None)
    end_year = data.get('end_year', None)
    citation_count = data.get('citation_count', None)
    authors = data.get('authors', None)
    published_in = data.get('published_in', None)

    if not query:
        return jsonify({"error": "No query provided"}), 400
    results = get_relevant_papers(query, start_year, end_year, citation_count, published_in, authors, model)
    end_time = datetime.datetime.now()
    logger.info(f"Request completed at: {end_time}")
    logger.info(f"Total execution time: {end_time - start_time}")
    json_strings = []
    for result in results:
        json_strings.append(vars(result))
        insert_data(data)
    return json_strings



@application.route('/askQuestion', methods=['POST'])
def ask_question():
    data = request.json
    logger.info(f"Received data: {request.data}")

    # Log the parsed JSON data
    logger.info(f"Parsed JSON: {request.json}")
    query_data = data.get('query', {})  # Access the 'query' dictionary
    logger.info(f"query_data: {query_data}")
    question = query_data.get('question')
    url = query_data.get('url')
    logger.info(f"url: {url}")
    answer = get_answer_from_paperqa([url], question)
    response = {
        "answer": answer
    }
    return jsonify(response)


@application.route('/getReferencedPaperInfo', methods=['POST'])
def get_referenced_paper_info():
    data = request.json
    paper = data.get('query', '')
    response = {
        "answer": ""
    }
    return jsonify(response)

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8000, debug=True)

