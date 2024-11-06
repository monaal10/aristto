import openai
import os

# Set up the OpenAI API client
openai.api_key = "sk-zFNU8L6Nkc1e-2VgAKoSB8tBcuEgJ140flDuDTc0muT3BlbkFJ_ChBKzjg63-HOPaPNczEzxWVoahtCUU9g1ZsZzBvgA"

# Function to query GPT-4
def query_gpt4_mini(user_query):
    try:
        # Make API call to GPT-4
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini-2024-07-18",  # Replace with the specific model you're using, if necessary
            messages=[
                {"role": "system", "content": "You are a research expert and so is the person that is going to read your response. Be highly technical and specific in your response to the query. Only answer the question based on the context provided. If you do not gwt the answer fromt the context provided say I dont know."},
                {"role": "user", "content": user_query}
            ]
        )
        # Extract the response from the model
        return response['choices'][0]['message']['content']

    except Exception as e:
        return f"An error occurred: {str(e)}"


