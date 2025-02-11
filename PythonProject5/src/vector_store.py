import uuid
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from src.config import QDRANT_HOST, QDRANT_API_KEY

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class VectorStore:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStore, cls).__new__(cls)
            cls._instance.client = QdrantClient(QDRANT_HOST, api_key=QDRANT_API_KEY, check_compatibility=False)
            cls._instance.collection_name = "embeddings"
            cls._instance.create_collection()
        return cls._instance

    def create_collection(self):
        """Create Qdrant collection if it doesn't exist."""
        collections = self.client.get_collections()
        if self.collection_name not in [c.name for c in collections.collections]:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )

    def insert_vector(self, vector, document_id, filename, metadata):
        """Insert a vector with metadata into Qdrant."""
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "document_id": document_id,
                "filename": filename,
                "metadata": metadata  # Only store metadata, not full text
            }
        )
        self.client.upsert(collection_name=self.collection_name, points=[point])
        logger.debug(f"✅ Vector inserted with metadata: {metadata}")

    def search_vector(self, query_vector, top_k=5, filters=None):
        """Retrieve relevant vectors from Qdrant with metadata filtering."""
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                with_payload=True,
                query_filter=filters  # ✅ Add metadata filtering
            )

            if not results:
                return []

            # Extract relevant information
            structured_results = [
                {
                    "document_id": result.payload.get("document_id"),  # ✅ Use document_id from payload
                    "score": result.score,
                    "payload": result.payload  # Keep full payload for debugging
                }
                for result in results
                if result.payload.get("document_id")  # ✅ Ensure document_id exists
            ]

            logger.debug(f"🔍 Search Results from Qdrant: {structured_results}")
            return structured_results

        except Exception as e:
            logger.error(f"❌ Error during vector search: {e}")
            return []
