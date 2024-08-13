import json

from flask import Flask, request, jsonify, render_template
import logging
import datetime
from concurrent.futures import ThreadPoolExecutor
import sys

from chat_with_paper_qa import get_answer
from extract_figures import get_figures_and_tables
from get_referenced_papers import fetch_referenced_papers
from get_relevant_papers import get_relevant_papers
# from classes.mongodb import MongoDB, insert_data
from flask_cors import CORS
import os
os.environ['OPENAI_API_KEY'] = 'sk-None-IEWqcLkHft3djH66AroZT3BlbkFJ4cCc3ieleT5ArR1On5rK'
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIA6ODU27KHAM2XYDGK'
os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# mongodbClient = MongoDB()
app = Flask(__name__)
application = app
CORS(app)


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


@app.route('/', methods=['GET'])
def main():
    return render_template("start-basic-search.html")


@app.route('/search', methods=['POST'])
def search():
    start_time = datetime.datetime.now()
    logger.info(f"Request received at: {start_time}")

    data = request.json
    query = data.get('query', '')

    if not query:
        return jsonify({"error": "No query provided"}), 400

    results = get_relevant_papers(query)
    end_time = datetime.datetime.now()
    logger.info(f"Request completed at: {end_time}")
    logger.info(f"Total execution time: {end_time - start_time}")
    json_strings = []
    for result in results:
        json_strings.append(vars(result))
    data = {
        "search_id": json_strings[0].get("search_id"),
        "user_id": json_strings[0].get("user_id"),
        "research_papers": json_strings
    }
    # insert_data(mongodbClient, data)
    return json_strings


@app.route('/getExpandedViewData', methods=['POST'])
def get_diagrams_and_referenced_papers():
    logger.info("Received request data: %s", request.data)
    data = request.json
    paper = data.get('query')
    if not paper:
        return jsonify({"error": "No paper provided"}), 400
    logger.info("Paper content: %s", json.dumps(paper, indent=2))
    with ThreadPoolExecutor() as executor:
        figures_future = executor.submit(get_figures_and_tables, paper)
        referenced_papers_future = executor.submit(fetch_referenced_papers, paper)
        figures = figures_future.result()
        logger.info("Got figures")
        referenced_papers = referenced_papers_future.result()
        logger.info("Got referenced papers")
        response = {
            "figures": figures,
            "referenced_papers": referenced_papers
        }

        return jsonify(response)


@app.route('/askQuestion', methods=['POST'])
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
    answer = get_answer([url], question)
    response = {
        "answer": answer
    }
    return jsonify(response)


@app.route('/getReferencedPaperInfo', methods=['POST'])
def get_referenced_paper_info():
    data = request.json
    paper = data.get('query', '')
    response = {
        "answer": ""
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)

