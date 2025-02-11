import logging
from src.vector_store import VectorStore
from src.document_store import DocumentStore
from src.embeddings import get_embedding
from src.llm import generate_response

class QueryEngine:
    def __init__(self):
        self.vector_store = VectorStore()
        self.document_store = DocumentStore()

    def query(self, query_text: str, top_k: int = 5):
        """
        Executes a retrieval-augmented query:
         1. Generates an embedding for the query.
         2. Retrieves similar vectors from Qdrant.
         3. Fetches full documents from MongoDB.
         4. Constructs a prompt for the LLM.
         5. Returns the generated response.

        :param query_text: The user query string.
        :param top_k: Number of documents to retrieve.
        :return: LLM-generated response.
        """
        try:
            # Step 1: Generate embedding for the query
            query_embedding = get_embedding(query_text)
            logger.debug("✅ Generated query embedding.")

            # Step 2: Retrieve similar vectors from Qdrant
            search_results = self.vector_store.search_vector(query_embedding, top_k=top_k)
            logger.debug(f"✅ Retrieved {len(search_results)} search results from Qdrant.")

            # Step 3: Retrieve full documents from MongoDB
            full_documents = []
            for result in search_results:
                doc_id = result.payload.get("document_id")
                if not doc_id:
                    logger.warning("⚠️ No document ID found in payload; skipping result.")
                    continue

                logger.debug(f"🔍 Searching MongoDB for document_id: {doc_id}")

                try:
                    document = self.document_store.get_document(doc_id)
                    logger.debug(f"🔍 Retrieved Document from MongoDB: {document}")

                    if document and "text" in document and document["text"].strip():
                        full_documents.append(document)
                except Exception as e:
                    logger.error(f"❌ Error retrieving document with ID {doc_id}: {e}")

            if not full_documents:
                logger.warning("⚠️ No valid documents retrieved; returning fallback response.")
                return "No relevant documents were found."

            # Step 4: Construct a clean context from retrieved documents
            context = "\n\n".join(doc.get("text", "").strip() for doc in full_documents if doc.get("text", "").strip())
            logger.debug(f"📝 Constructed Context Before LLM Call:\n{context}")

            if not context.strip():
                logger.warning("⚠️ Retrieved documents contain no meaningful text.")
                return "No relevant context was found in the retrieved documents."

            # Step 5: Build prompt for LLM
            prompt = f"""
            You are an AI assistant that answers user queries based on provided context. 
            Use the following retrieved information to answer the question concisely:

            Context:
            {context}

            Question:
            {query_text}

            Provide a well-structured response based only on the context.
            """
            logger.debug(f"📜 Final Prompt Sent to LLM:\n{prompt}")

            # Step 6: Generate the response using LLM
            response_text = generate_response(prompt)
            logger.debug("✅ Received response from the language model.")

            return response_text

        except Exception as e:
            logger.error(f"❌ Error during query execution: {e}")
            return "An error occurred while processing your query."