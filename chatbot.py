import anthropic
import logging
import getpass
import time
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain.memory import ChatMessageHistory
# Configure the logger
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    def provide_context(self, context,chunks):
        """
        Add context to the ChatBot's memory.
        The context can be added using text chunks from any source (e.g., PDF chunks).
        """
        template = """  
            you are a chatbot
            Previous Conversation:
            {memory.messages}
            U will be answer questions based on {chunks}
"""
        self.memory.add_user_message(template)
        self.memory.append(context)  # Append context chunks to memory
        logger.info(f"Context added to bot: {context}")
    def add_memory_fromchat(self,role,message_to_add):
        match role:
            case "user": 
                self.memory.add_user_message(message_to_add)
            case "assistant":
                self.memory.add_ai_message(message_to_add)   
    def ask_question(self, question, temperature=0.3):
        """
        Ask the chatbot a question; it will respond using the provided context.
        """
        start_time = time.time()
        client = self.client
        self.add_memory_fromchat("user",question)
        response = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens
    =512,
    temperature = temperature,
    messages=self.memory.messages
)
        end_time = time.time()
        logger.info(f"Time to get answer - {end_time - start_time}")
        return response.content[0].text

# Example usage:
if __name__ == "__main__":
    chunks = """
 68723108-cfbb-490b-a6b5-64fa86b826a8 - ('work. Supervised learning in the form of regression (for continuous outputs) and classiﬁcation (for discrete outputs) is an important constituent of stati stics and machine learning, either for analysis of data sets, or as a subgoal of a more complex problem. Traditionally parametric1models have been used for this purpose. These have a possible advantage in ease of interpretability, but for complex data sets, simple parametric models may lack expressive power, and their more complex counter- parts (such as feed forward neural networks) may not be easy to work with in practice. The advent of kernel machines, such as Support Vector', 0.20118671239969016)
2024-10-21 11:28:34,904 - download_pdf - INFO - 51770a85-891e-40d1-9c4a-a8d0651cfb8b - ('some questions unanswered: How do we come up with mean and covariance functions in the ﬁrst place? How could we estimate the noise level? This is the topic of the next section. 3 Training a Gaussian Process In the previous section we saw how to update the prior Gaussian process in the light of training data. This is useful if we have enough prior information ab out a dataset at hand to conﬁdently specify prior mean and covariance functions. However, the availability of such detailed prior information is not the ty pical case in machine learning applications. In order for', 0.16268811316702103)
2024-10-21 11:28:34,904 - download_pdf - INFO - 97dd8d8e-e2b9-4610-8d51-cf9dc4fb6408 - ('sampling techniques [5]. Another issue is the computational limitations. A straightforward impl emen- tation of the simple techniques explained here, requires inversion of the covari- ance matrix Σ, with a memory complexity of O(n2) and a computational com- plexity ofO(n3). This is feasible on a desktop computer for dataset sizes of n 9The covariance function must be positive deﬁnite to ensure that th e resulting co- variance matrix is positive deﬁnite.Gaussian Processes 75 up to a few thousands. Although there are many interesting machine learning problems with such relatively small datasets, a lot of current work is goi ng into', 0.13247267940140905)
"""
    bot = Chatbot()
    # bot.provide_context("This is some context.")
    # bot.add_memory_from_chunks(chunks)
    print("got here")
    # bot.set_bot_context("You will receive chunks of research papers with chunk IDs. Return answers to follow-up questions, referencing the chunk IDs used. Format responses in JSON")
    response = bot.ask_question("what must the covariance function be, positive or negative and what are imp constituents of statistics")
    print(response)
    # bot.reset_memory()
