from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
import os
from dotenv import load_dotenv

load_dotenv()

CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "documents"


def get_embeddings_model():
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        task_type="retrieval_document"
    )


def store_chunks_in_chroma(chunks: list[Document]):
    embeddings = get_embeddings_model()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH,
        collection_name=COLLECTION_NAME
    )

    print(f"✅ Stored {len(chunks)} chunks in ChromaDB")
    return vectorstore


def get_vectorstore():
    embeddings = get_embeddings_model()
    return Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )


def retrieve_relevant_chunks(question: str, k: int = 4):
    # For querying, use retrieval_query (different from retrieval_document used for storage)
    query_embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        task_type="retrieval_query"
    )
    
    vectorstore = Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=query_embeddings,
        collection_name=COLLECTION_NAME
    )

    relevant_chunks = vectorstore.similarity_search(question, k=k)
    print(f"✅ Retrieved {len(relevant_chunks)} chunks for: '{question}'")
    return relevant_chunks