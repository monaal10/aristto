import time
from typing import Dict

from openai import RateLimitError


def get_model_response(llm, prompt: str, state: Dict):
    num_retries = 3  # Maximum number of retries
    retry_delay = 60  # Delay in seconds before retrying

    for i in range(num_retries):
        try:
            messages = [{
                "role": "user",
                "content": prompt.format(**state).encode("utf-8", "replace").decode("utf-8")
            }]
            response = llm.invoke(messages)
            return response

        except Exception as e:
            if isinstance(e, RateLimitError):
                if i < num_retries - 1:
                    print(f"Rate limit reached, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    raise Exception(f"Error in API call after {num_retries} retries: {e}")
            else:
                raise Exception(f"Error in API call: {e}")
