# ingest.py — Handles reading PDFs and splitting them into chunks

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os


def load_and_chunk_document(file_path: str):
    """
    Takes a PDF file path.
    Returns a list of text chunks ready for embedding.
    """

    # --- Step 1: Load the PDF ---
    # PyPDFLoader reads each page of the PDF and returns a list of "Document" objects
    # Each Document has: page_content (the text) + metadata (page number, source)
    loader = PyPDFLoader(file_path)
    pages = loader.load()

    print(f"Loaded {len(pages)} pages from {file_path}")

    # --- Step 2: Split into chunks ---
    # WHY CHUNK? LLMs have a "context window" limit (e.g., GPT-4 can take ~128k tokens).
    # But we don't want to send the ENTIRE document every time — that's expensive and slow.
    # We only want the RELEVANT parts. So we break it into small chunks,
    # embed each chunk, and later retrieve only relevant ones.

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,       # Each chunk = max 500 characters
        chunk_overlap=50,     # 50 chars overlap between chunks (so context isn't cut off at edges)
        separators=["\n\n", "\n", ".", " "]  # Try to split at paragraph > line > sentence > word
    )

    chunks = text_splitter.split_documents(pages)

    print(f"Split into {len(chunks)} chunks")

    # Each chunk looks like:
    # Document(page_content="...text...", metadata={"source": "file.pdf", "page": 2})

    return chunks