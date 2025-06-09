import logging
import time
from typing import Dict

from openai import RateLimitError, BadRequestError

logger = logging.getLogger(__name__)
def get_model_response(llm, prompt: str, state: Dict):
    num_retries = 3
    retry_delay = 60
    trim_factor = 0.8  # Reduce length by 20% each time

    formatted_prompt = prompt.format(**state).encode("utf-8", "replace").decode("utf-8")

    for i in range(num_retries):
        try:
            messages = [{"role": "user", "content": formatted_prompt}]
            response = llm.invoke(messages)
            return response

        except Exception as e:
            if isinstance(e, BadRequestError):
                if "This model's maximum context length is" in str(e):
                    # Trim the prompt length and retry
                    formatted_prompt = formatted_prompt[:int(len(formatted_prompt) * trim_factor)]
                    logger.info(f"Context length exceeded, trimming message to {len(formatted_prompt)} characters...")
                    continue
            elif isinstance(e, RateLimitError):
                if i < num_retries - 1:
                    logger.info(f"Rate limit reached, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    raise Exception(f"Error in API call after {num_retries} retries: {e}")
            else:
                raise Exception(f"Error in API call: {e}")

