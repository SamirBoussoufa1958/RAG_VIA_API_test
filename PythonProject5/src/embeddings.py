import os
import openai
from dotenv import load_dotenv
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_embedding(text: str, model: str = "text-embedding-3-small") -> list:
    """
    Generate an embedding for the input text using OpenAI's API.

    Parameters:
        text (str): The text to be embedded.
        model (str): The OpenAI embedding model to use.

    Returns:
        list: The generated embedding as a list of floats.
    """

    text = text.replace("\n", " ")  # Ensure consistency
    response = openai.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

