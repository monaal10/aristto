from langchain_google_vertexai import ChatVertexAI
from main.utils.constants import AZURE_OPENAI_4o_MINI_ENDPOINT, AZURE_OPENAI_4o_MINI_API_KEY, AZURE_OPENAI_4_ENDPOINT, \
    AZURE_OPENAI_4_API_KEY, AZURE_OPENAI_4o_API_KEY, AZURE_OPENAI_4o_ENDPOINT, GEMINI_API_KEY, OPENAI_API_KEY, \
    ANTHROPIC_API_KEY, AZURE_OPENAI_o3_API_KEY, AZURE_OPENAI_o3_MINI_ENDPOINT
from langchain_openai import AzureChatOpenAI
from langchain_anthropic import ChatAnthropic

def get_openai_4o_mini():
    try:
        return AzureChatOpenAI(
            api_key=AZURE_OPENAI_4o_MINI_API_KEY,
            azure_endpoint=AZURE_OPENAI_4o_MINI_ENDPOINT,
            api_version="2024-08-01-preview",
            temperature=0.2,
            timeout=None,
            max_retries=2,
            azure_deployment="gpt-4o-mini-2",
            model="gpt-4o-mini"
        )
    except Exception as e:
        raise Exception(f"Failed to get openai 4o-mini: {e}")


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
        raise Exception(f"Failed to get openai gpt-4: {e}")


def get_openai_4o():
    try:
        return AzureChatOpenAI(
            api_key=AZURE_OPENAI_4o_API_KEY,
            azure_endpoint=AZURE_OPENAI_4o_ENDPOINT,
            api_version="2024-08-01-preview",
            temperature=0.2,
            max_tokens=16384,
            timeout=None,
            max_retries=2,
            azure_deployment="gpt-4o",
            model="gpt-4o"
        )
    except Exception as e:
        raise Exception(f"Failed to get openai 4o-mini: {e}")


def get_gemini_flash_2():
    try:
        return ChatVertexAI(
            model="gemini-2.0-flash-001",
            temperature=0,
            max_tokens=None,
            max_retries=6,
            stop=None,
            project="gen-lang-client-0118493585")
    except Exception as e:
        raise Exception(f"Failed to get gemini flash 2.0: {e}")


def get_o3_mini():
    try:
        return AzureChatOpenAI(
            api_key=AZURE_OPENAI_o3_API_KEY,
            azure_endpoint=AZURE_OPENAI_o3_MINI_ENDPOINT,
            api_version="2024-12-01-preview",
            timeout=None,
            max_retries=2,
            azure_deployment="o3-mini",
            model="o3-mini",
            reasoning_effort="low"
        )
    except Exception as e:
        raise Exception(f"Failed to get openai o3-mini: {e}")

def get_o3_mini_medium():
    try:
        return AzureChatOpenAI(
            api_key=AZURE_OPENAI_o3_API_KEY,
            azure_endpoint=AZURE_OPENAI_o3_MINI_ENDPOINT,
            api_version="2024-12-01-preview",
            timeout=None,
            max_retries=2,
            azure_deployment="o3-mini",
            model="o3-mini",
            reasoning_effort="medium"
        )
    except Exception as e:
        raise Exception(f"Failed to get openai o3-mini: {e}")


def get_o3_mini_high():
    try:
        return AzureChatOpenAI(
            api_key=AZURE_OPENAI_o3_API_KEY,
            azure_endpoint=AZURE_OPENAI_o3_MINI_ENDPOINT,
            api_version="2024-12-01-preview",
            timeout=None,
            max_retries=2,
            azure_deployment="o3-mini",
            model="o3-mini",
            reasoning_effort="high"
        )
    except Exception as e:
        raise Exception(f"Failed to get openai o3-mini: {e}")

def get_claude():
    return  ChatAnthropic(
    model="claude-3-7-sonnet-latest",
    temperature=0,
    timeout=None,
    max_retries=2,
    api_key=ANTHROPIC_API_KEY,
)