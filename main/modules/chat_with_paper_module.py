import json

import anthropic
import logging
import getpass
import time

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from pymongo import MongoClient
from datetime import datetime
from langchain.memory import ChatMessageHistory
from langchain_anthropic import ChatAnthropic

from prompts.answer_a_question_prompts import ANSWER_A_QUESTION_PROMPT

# Configure the logger
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB Atlas connection
MONGO_URI = ""
client = MongoClient(MONGO_URI)
db = client['chatbot_db']
chat_history_collection = db['chat_history']

# API key for the Anthropic chatbot
api_key = "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"

model = ChatAnthropic(model="claude-3-5-sonnet-20240620", api_key=api_key)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            ANSWER_A_QUESTION_PROMPT,
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)


def chat(query, relevant_chunks):
    prompt_template = PromptTemplate.from_template(ANSWER_A_QUESTION_PROMPT)
    prompt = prompt_template.invoke({"question": {query}, "reference_list": json.dumps(relevant_chunks)})
    output = model.invoke(prompt)
    return output
