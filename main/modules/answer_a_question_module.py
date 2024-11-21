import json
from langchain_core.prompts import PromptTemplate
from classes.answer_a_question_classes import Answer, AskQuestionOutput, AnswerReference
from prompts.answer_a_question_prompts import ANSWER_A_QUESTION_PROMPT

from utils.anthropic_utils import get_claude_haiku


def construct_final_output(output, papers_with_chunks):
    try:
        references = []
        answer = output.answer
        for reference_id in output.reference_ids:
            paper_id = reference_id.split("_")[0]
            for paper in papers_with_chunks:
                if paper.open_alex_id == paper_id:
                    chunks = paper.pdf_content_chunks
                    reference_text = chunks.get(reference_id, "")
                    reference = AnswerReference(reference_text=reference_text, reference_id=reference_id, paper=paper)
                    references.append(reference)
        return AskQuestionOutput(references=references, answer=answer)
    except Exception as e:
        raise RuntimeError(f"Failed to construct final output  {e}")


def answer_a_question(query, relevant_chunks, papers_with_chunks):
    try:
        model = get_claude_haiku()
        structured_model = model.with_structured_output(Answer)
        prompt_template = PromptTemplate.from_template(ANSWER_A_QUESTION_PROMPT)
        prompt = prompt_template.invoke({"question": {query}, "reference_list": json.dumps(relevant_chunks)})
        output = structured_model.invoke(prompt)
        formatted_output = construct_final_output(output, papers_with_chunks)
        return formatted_output
    except Exception as e:
        raise f"Failed to answer question {query}: {e}"
