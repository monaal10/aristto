import re

from langchain_core.prompts import PromptTemplate

from main.modules.semantic_scholar_index_module import get_papers_from_semantic_scholar
from main.modules.open_alex_index_module import get_relevant_papers_from_open_alex
from main.classes.answer_a_question_classes import Answer, AskQuestionOutput, AnswerReference, SearchableQueryAndTitle
from main.prompts.answer_a_question_prompts import ANSWER_A_QUESTION_PROMPT, GENERATE_SEARCHABLE_QUERY
from main.utils.llm_utils import get_o41_mini
import json
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

model = get_o41_mini()


def construct_final_output(output, context, relevant_papers):
    try:
        references = []
        used_ids = set()
        reference_ids = re.findall(r'\[(.*?)\]', output)
        for paper in context:
            for reference_id in reference_ids:
                if str(paper.get("uuid")) == reference_id and reference_id not in used_ids:
                    reference_text = paper.get("text")
                    reference = AnswerReference(reference_text=reference_text, reference_id=reference_id,
                                                paper=paper.get("paper_metadata"))
                    used_ids.add(reference_id)
                    references.append(reference)
        return AskQuestionOutput(references=references, answer=output, relevant_papers=relevant_papers)
    except Exception as e:
        raise RuntimeError(f"Failed to construct final output  {e}")


def generate_searchable_query(query, conversation_history):
    try:
        generate_query_prompt = PromptTemplate.from_template(GENERATE_SEARCHABLE_QUERY)
        final_prompt = generate_query_prompt.invoke({"query": query, "conversation_history": conversation_history})
        structured_model = model.with_structured_output(SearchableQueryAndTitle)
        response = structured_model.invoke(final_prompt)
        return response
    except Exception as e:
        raise RuntimeError(f"Failed to get title and searchable query {e}")

def get_relevant_context(query, start_year, end_year, citation_count, authors, published_in, sjr):
    try:
        context, relevant_papers = get_papers_from_semantic_scholar(
            query, start_year, end_year, citation_count, authors, published_in, sjr
        )
        # Then call get_papers_from_open_alex
        oa_context, oa_relevant_papers = get_relevant_papers_from_open_alex(
            query, start_year, end_year, citation_count, authors, published_in, sjr, [], False
        )

        # Combine results (using only first 10 items from each context)
        combined_context = context[:5] + oa_context[:10]
        combined_relevant_papers = relevant_papers + oa_relevant_papers
        return {"context": combined_context, "relevant_papers": combined_relevant_papers}
    except Exception as e:
        raise Exception(e)


def invoke_agent(query, start_year, end_year, citation_count, authors, published_in, sjr, conversation_history):
    try:
            response = generate_searchable_query(query, conversation_history[-5:])
            searchable_query = response.searchable_query
            title = response.title

            relevant_context = get_relevant_context(searchable_query, start_year, end_year, citation_count, authors,
                                                            published_in, sjr)
            context = relevant_context["context"]
            relevant_papers = [paper.get("paper_metadata") for paper in relevant_context["relevant_papers"]]

            filtered_context = []
            for paper in context:
                filtered_context.append({'id': str(paper.get("uuid")), 'text': paper.get("text")})
            if len(filtered_context) == 0:
                no_papers_found_answer = "No relevent papers found, please update your search query/filters"
                conversation_history.append(("human", query))
                conversation_history.append(("assistant", no_papers_found_answer))
                return AskQuestionOutput(
                    references=[], answer=no_papers_found_answer, relevant_papers=[]), conversation_history, title
            prompt_template = PromptTemplate.from_template(ANSWER_A_QUESTION_PROMPT)
            prompt = prompt_template.invoke({"question": {query}, "reference_list": json.dumps(filtered_context),
                                            "conversation_history": json.dumps(conversation_history[-5:])})

            output = model.invoke(prompt).content

            formatted_output = construct_final_output(output, context, relevant_papers)
            conversation_history.append(("human", query))
            conversation_history.append(("assistant", output))
            return formatted_output, conversation_history, title

    except Exception as e:
        raise RuntimeError(f"Failed to get agent response  {e}")


"""query = ("Give me a comprehensive lit review on the topic undulatory ﬁn motions in ﬁsh-like robots. Give me field "
         "progression, methodologies and comparisons, some research gaps and any other section you feel is important to "
         "know for a researcher.")
answer = invoke_agent(query, None, None, None, [], [], [], [])
print()"""

