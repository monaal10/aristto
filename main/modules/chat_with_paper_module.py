import logging
from langchain_core.prompts import PromptTemplate

from main.prompts.chat_with_paper_prompts import CHAT_WITH_PAPER_PROMPT
from main.utils.anthropic_utils import get_claude_haiku
from main.utils.azure_openai_utils import get_openai_4o_mini

# Configure the logger
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def chat(query, relevant_chunks, conversation_history):
    model = get_openai_4o_mini()
    prompt_template = PromptTemplate.from_template(CHAT_WITH_PAPER_PROMPT)
    references = []
    for chunk in relevant_chunks:
        references.append({chunk["title"]: chunk["chunk_text"]})
    prompt = prompt_template.invoke({"question": {query}, "references": references,
                                     "conversation_history": conversation_history})
    output = model.invoke(prompt)
    return output
