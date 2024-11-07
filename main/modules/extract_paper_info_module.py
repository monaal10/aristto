from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate

from classes.extract_paper_info_classes import ExtractedPaperInformation
from prompts.extract_paper_info_prompts import EXTRACT_PAPER_INFO_PROMPT

from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-3-5-haiku-latest",
                    api_key="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",
                    temperature=0,
                    max_tokens=4096,
                    timeout=None)

api_key = "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"
model = ChatAnthropic(model="claude-3-5-sonnet-20240620", api_key=api_key)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            EXTRACT_PAPER_INFO_PROMPT,
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)


def extract_paper_information(pdf_content):
    try:
        structured_model = model.with_structured_output(ExtractedPaperInformation)
        prompt_template = PromptTemplate.from_template(EXTRACT_PAPER_INFO_PROMPT)
        prompt = prompt_template.invoke({"pdf_content": pdf_content})
        output = structured_model.invoke(prompt)
        return output
    except Exception as e:
        raise f"Error in information extraction: {e}"
