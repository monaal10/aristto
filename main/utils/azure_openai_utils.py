from utils.constants import AZURE_OPENAI_4o_MINI_ENDPOINT, AZURE_OPENAI_4o_MINI_API_KEY, AZURE_OPENAI_4_ENDPOINT, \
    AZURE_OPENAI_4_API_KEY

from langchain_openai import AzureChatOpenAI
import os

def get_openai_4o_mini():
    try:
        return AzureChatOpenAI(
            api_key=AZURE_OPENAI_4o_MINI_API_KEY,
            azure_endpoint=AZURE_OPENAI_4o_MINI_ENDPOINT,
            api_version="2024-08-01-preview",
            temperature=0.2,
            max_tokens=16384,
            timeout=None,
            max_retries=2,
            azure_deployment="gpt-4o-mini",
            model="gpt-4o-mini"
        )
    except Exception as e:
        raise f"Failed to get openai 4o-mini: {e}"

def get_openai_gpt4():
    try:
        return AzureChatOpenAI(
            api_key=AZURE_OPENAI_4_API_KEY,
            azure_endpoint=AZURE_OPENAI_4_ENDPOINT,
            api_version="2024-08-01-preview",
            temperature=0,
            max_tokens=4096,
            timeout=None,
            max_retries=2,
            azure_deployment="gpt-4",
            model="gpt-4",
            model_version="1106-Preview"
        )
    except Exception as e:
        raise f"Failed to get openai gpt-4: {e}"
