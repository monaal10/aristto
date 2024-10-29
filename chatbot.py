import anthropic
import logging
import getpass
import time
from pymongo import MongoClient
from datetime import datetime
from langchain.memory import ChatMessageHistory
from langchain_anthropic import ChatAnthropic

# Configure the logger
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB Atlas connection
MONGO_URI = "your_mongo_atlas_connection_string"
client = MongoClient(MONGO_URI)
db = client['chatbot_db']
chat_history_collection = db['chat_history']

# API key for the Anthropic chatbot
api_key = "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"

class Chatbot:

    def __init__(self, temperature=0):
        """Initialize the Chatbot with an API key and optional temperature for responses."""
        self.api_key = api_key
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.memory = ChatMessageHistory()
        self.context = ""
        self.api_key = getpass.getpass()
        self.model = ChatAnthropic(model="claude-3-5-sonnet-20240620")

    def save_to_database(self, role, message):
        """Save a message to MongoDB Atlas."""
        chat_history_collection.insert_one({
            "role": role,
            "message": message,
            "timestamp": datetime.utcnow()
        })
        logger.info(f"Message saved to database - Role: {role}, Message: {message}")

    def load_chat_history(self):
        """Load chat history from MongoDB Atlas."""
        history = chat_history_collection.find().sort("timestamp", 1)
        for entry in history:
            role = entry["role"]
            message = entry["message"]
            if role == "user":
                self.memory.add_user_message(message)
            elif role == "assistant":
                self.memory.add_ai_message(message)

    def add_memory_fromchat(self, role, message_to_add):
        """Add a message to the chatbot's memory and save it to the database."""
        if role == "user":
            self.memory.add_user_message(message_to_add)
        elif role == "assistant":
            self.memory.add_ai_message(message_to_add)
        self.save_to_database(role, message_to_add)

    def ask_question(self, question, temperature=0.3):
        """
        Ask the chatbot a question; it will respond using the provided context.
        """
        start_time = time.time()
        client = self.client
        self.add_memory_fromchat("user", question)

        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=512,
            temperature=temperature,
            messages=self.memory.messages
        )

        response_text = response.content[0].text
        self.add_memory_fromchat("assistant", response_text)
        end_time = time.time()

        logger.info(f"Time to get answer - {end_time - start_time}")
        return response_text

# Example usage
if __name__ == "__main__":
    bot = Chatbot()
    bot.load_chat_history()  # Load previous conversation history
    response = bot.ask_question("What are the important constituents of statistics?")
    print(response)
