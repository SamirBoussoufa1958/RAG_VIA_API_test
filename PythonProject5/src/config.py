import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

# Qdrant
QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


