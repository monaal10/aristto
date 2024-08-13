import openai
import os

# Set up the OpenAI API client
openai.api_key = "sk-None-IEWqcLkHft3djH66AroZT3BlbkFJ4cCc3ieleT5ArR1On5rK"


def call_chatgpt_assistant(assistant_id, user_message):
        # Create a thread
        thread = openai.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": user_message,
                    "attachments": []
                }])

        run = openai.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
        messages = openai.beta.threads.messages.list(thread_id=thread.id)

        # The latest message will be the assistant's response
        assistant_response = messages.data[0].content[0].text.value
        print(assistant_response)
        # Retrieve the assistant's response
        #messages = openai.beta.threads.retrieve(thread_id=run.id)
        assistant_response = ""
        #assistant_response = messages.data[0].content[0].text.value

        return assistant_response


def main():
    assistant_id = "asst_Dtjr12HPLBh4xnGjklAvEatZ"
    user_message = "Here is the url of the paper : https://arxiv.org/pdf/2312.10997. What is the best method for RAG according to this paper and why?"
    response = call_chatgpt_assistant(assistant_id, user_message)
    if response:
        print("Assistant's response:", response)


main()
