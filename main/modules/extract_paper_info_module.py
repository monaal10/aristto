from langchain_core.prompts import PromptTemplate
from main.classes.extract_paper_info_classes import ExtractedPaperInformation
from main.prompts.extract_paper_info_prompts import EXTRACT_PAPER_INFO_PROMPT
from main.utils.azure_openai_utils import get_openai_4o_mini


def extract_paper_information(pdf_content):
    try:
        model = get_openai_4o_mini()
        structured_model = model.with_structured_output(ExtractedPaperInformation)
        prompt_template = PromptTemplate.from_template(EXTRACT_PAPER_INFO_PROMPT)
        prompt = prompt_template.invoke({"pdf_content": pdf_content})
        output = structured_model.invoke(prompt)
        return output
    except Exception as e:
        raise f"Error in information extraction: {e}"
