# main.py — The FastAPI web server that ties everything together

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os

from ingest import load_and_chunk_document
from retriever import store_chunks_in_chroma, retrieve_relevant_chunks
from llm import get_llm_answer

app = FastAPI(title="RAG Document Q&A API")

# CORS — allows your React frontend (running on port 3000) to call this API (port 8000)
# Without this, the browser blocks cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# --- Request/Response Models (Pydantic) ---
# Pydantic validates incoming JSON automatically — like Zod in TypeScript

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    sources: list[dict]


# --- Endpoints ---

@app.get("/")
def root():
    return {"message": "RAG Document Q&A API is running!"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF → ingest → chunk → embed → store in ChromaDB.
    After this, the document is "queryable".
    """
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Save uploaded file temporarily
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Process the document
        chunks = load_and_chunk_document(file_path)
        store_chunks_in_chroma(chunks)

        return {
            "message": f"Document '{file.filename}' processed successfully",
            "chunks_created": len(chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question → retrieve relevant chunks → get LLM answer.
    This is the core RAG flow.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # Retrieve relevant chunks from ChromaDB
    relevant_chunks = retrieve_relevant_chunks(request.question, k=4)

    # Get answer from LLM using retrieved context
    result = get_llm_answer(request.question, relevant_chunks)

    return AnswerResponse(
        answer=result["answer"],
        sources=result["sources"]
    )


@app.delete("/reset")
async def reset_database():
    """Clear ChromaDB — useful for testing with new documents."""
    import shutil
    if os.path.exists("./chroma_db"):
        shutil.rmtree("./chroma_db")
    return {"message": "Vector database cleared"}