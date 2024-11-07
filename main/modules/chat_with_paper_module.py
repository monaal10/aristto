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
from utils.anthropic_utils import get_claude_haiku

# Configure the logger
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
def chat(query, relevant_chunks):
    model = get_claude_haiku()
    prompt_template = PromptTemplate.from_template(ANSWER_A_QUESTION_PROMPT)
    prompt = prompt_template.invoke({"question": {query}, "reference_list": json.dumps(relevant_chunks)})
    output = model.invoke(prompt)
    return output
