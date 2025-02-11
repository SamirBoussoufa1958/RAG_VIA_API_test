import os
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import  ObjectId
# Load environment variables from .env
load_dotenv()

# Get MongoDB config
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")  # Default to 'test' if not set


class DocumentStore:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB_NAME]
        self.collection = self.db["documents"]
        print("✅ Connected to MongoDB:", self.db.list_collection_names())


    def insert_document(self, full_document):
        """
        Insert a full document (with metadata) into MongoDB.

        Parameters:
            doc_id (str): Unique document identifier.
            full_document (dict): Document data including text and metadata.
        """
        try:
            result = self.collection.insert_one(full_document)
            print(f"✅ Document inserted with _id: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            print("❌ Error inserting document:", e)
            raise e

    def get_document(self, document_id, fetch_full=True):
        projection = {"text": 1, "document_id": 1} if fetch_full else {"_id":0}
        # Query using the field name that matches your payload
        document = self.collection.find_one({"document_id": document_id}, projection)

        if document is None:
            raise Exception(f"Document with id {document_id} not found.")

        if "_id" in document:
            document["_id"] = str(document["document_id"])

        return document

    def close_connection(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            print("🛑 MongoDB connection closed.")


# Test MongoDB Connection and get_document functionality
if __name__ == "__main__":
    store = DocumentStore()
    # Use an existing document ID for testing or insert one first
    test_doc_id = "your-test-document-id"
    try:
        document = store.get_document(test_doc_id, fetch_full=True)
        print("Document retrieved:", document)
    except Exception as e:
        print(e)
    store.close_connection()

