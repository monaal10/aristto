from langchain_anthropic import ChatAnthropic

from main.utils.constants import CLAUDE_HAIKU_NAME, ANTHROPIC_API_KEY


def get_claude_haiku():
    try:
        return ChatAnthropic(model=CLAUDE_HAIKU_NAME,
                         api_key=ANTHROPIC_API_KEY,
                         temperature=0,
                         max_tokens=4096,
                         timeout=None)
    except Exception as e:
        raise f"Failed to get claude haiku model: {e}"
