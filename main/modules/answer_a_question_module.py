import json
from typing import List

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.messages import trim_messages
from langchain_core.prompts import PromptTemplate

from classes.answer_a_question_classes import Answer, AskQuestionOutput
from prompts.answer_a_question_prompts import ANSWER_A_QUESTION_PROMPT

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_anthropic import ChatAnthropic

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


def construct_final_output(output, papers_with_chunks):
    papers = []
    answer = output["answer"]
    for reference_id in output["reference_ids"]:
        paper_id = reference_id.split("_")[0]
        for paper in papers_with_chunks:
            if paper.oa_url == paper_id:
                papers.append(paper)
    return AskQuestionOutput(papers=papers, answer=answer)


def answer_a_question(query, relevant_chunks, papers_with_chunks):
    structured_model = model.with_structured_output(Answer)
    prompt_template = PromptTemplate.from_template(ANSWER_A_QUESTION_PROMPT)
    prompt = prompt_template.invoke({"question": {query}, "reference_list": json.dumps(relevant_chunks)})
    output = structured_model.invoke(prompt)
    formatted_output = construct_final_output(output, papers_with_chunks)
    return formatted_output
