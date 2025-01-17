import time
from typing import Dict

from openai import RateLimitError


def split_text_into_chunks(text: str, max_tokens: int = 100000) -> list:
    """Split text into chunks that are below the max token limit."""
    # Rough estimation: 1 token ≈ 4 characters for English text
    chars_per_chunk = max_tokens * 4
    chunks = []

    while len(text) > chars_per_chunk:
        # Find the last complete sentence within the chunk
        split_point = text[:chars_per_chunk].rfind('.')
        if split_point == -1:  # If no sentence end found, split at last space
            split_point = text[:chars_per_chunk].rfind(' ')
        if split_point == -1:  # If no space found, force split at chunk size
            split_point = chars_per_chunk

        chunks.append(text[:split_point + 1])
        text = text[split_point + 1:].lstrip()

    if text:  # Add remaining text as final chunk
        chunks.append(text)

    return chunks


def get_model_response(llm, prompt: str, state: Dict):
    num_retries = 3
    retry_delay = 60
    max_tokens = 120000

    formatted_prompt = prompt.format(**state).encode("utf-8", "replace").decode("utf-8")

    for i in range(num_retries):
        try:
            try:
                messages = [{"role": "user", "content": formatted_prompt}]
                response = llm.invoke(messages)
                # Extract the string content from the response
                return response.content if hasattr(response, 'content') else str(response)

            except Exception as e:
                if "context_length_exceeded" in str(e):
                    print("Context length exceeded, splitting into chunks...")
                    chunks = split_text_into_chunks(formatted_prompt, max_tokens)
                    combined_response = []

                    for chunk in chunks:
                        messages = [{"role": "user", "content": chunk}]
                        chunk_response = llm.invoke(messages)
                        # Extract the string content from each chunk response
                        chunk_content = chunk_response.content if hasattr(chunk_response, 'content') else str(
                            chunk_response)
                        combined_response.append(chunk_content)

                    return "\n".join(combined_response)
                else:
                    raise e

        except RateLimitError:
            if i < num_retries - 1:
                print(f"Rate limit reached, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
            else:
                raise Exception(f"Error in API call after {num_retries} retries: Rate limit exceeded")
        except Exception as e:
            raise Exception(f"Error in API call: {e}")
