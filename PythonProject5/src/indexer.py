import os
import hashlib
import logging
import pymupdf # PyMuPDF for PDFs
from docx import Document
import io
from dotenv import load_dotenv
from llama_index.core.node_parser import TokenTextSplitter
from src.embeddings import get_embedding
from src.vector_store import VectorStore
from llama_parse import LlamaParse

# Load environment variables
load_dotenv()
LLAMA_PARSE_API_KEY = os.getenv("LLAMA_PARSE_API_KEY")

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize LlamaParse
parser = LlamaParse(api_key=LLAMA_PARSE_API_KEY, result_type="json")

# Configure chunking
text_splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=50)

def generate_document_id(file_name: str) -> str:
    """Generate a consistent document ID based on filename hash."""
    return hashlib.md5(file_name.encode()).hexdigest()

def extract_text_from_file(file_bytes: bytes, file_type: str) -> str:
    logger.debug(f"📤 Extracting text from file type: {file_type}")

    try:
        text = ""

        if file_type == "text/plain":
            text = file_bytes.decode("utf-8", errors="ignore")
            logger.debug(f"📝 Extracted text length: {len(text)} (TXT)")

        elif file_type == "application/pdf":
            with pymupdf.open(stream=file_bytes, filetype="pdf") as pdf_doc:
                text = "\n".join(page.get_text("text") for page in pdf_doc)
            logger.debug(f"📄 Extracted text length: {len(text)} (PDF)")

        elif file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            doc = Document(io.BytesIO(file_bytes))
            text = "\n".join([para.text for para in doc.paragraphs])
            logger.debug(f"📑 Extracted text length: {len(text)} (DOCX)")

        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        if not text.strip():
            raise ValueError("No readable text found in document.")

        return text.strip()

    except Exception as e:
        logger.error(f"❌ Error extracting text from {file_type}: {e}")
        raise ValueError(f"Extraction failed: {e}")


def process_document(file_bytes: bytes, filename: str, file_type: str):
    logger.debug(f"📄 process_document() called for: {filename}, type: {file_type}")

    document_id = generate_document_id(filename)
    logger.debug(f"📜 Generated Document ID: {document_id}")

    try:
        full_text = extract_text_from_file(file_bytes, file_type)
        logger.debug(f"📝 Extracted text: {len(full_text)} characters")

        chunks = text_splitter.split_text(full_text)
        logger.debug(f"🔗 Chunked into {len(chunks)} pieces")

        return document_id, full_text, chunks
    except Exception as e:
        logger.error(f"❌ Error processing document {filename}: {e}")
        raise

