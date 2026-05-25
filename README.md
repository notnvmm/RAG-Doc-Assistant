# RAG Document Q&A Assistant

Ask natural language questions about any PDF document using Retrieval-Augmented Generation (RAG).

## Architecture

- **Frontend**: React.js + TypeScript
- **Backend**: FastAPI (Python)
- **Embeddings**: Google Gemini (`gemini-embedding-001`)
- **Vector Store**: ChromaDB
- **LLM**: Google Gemini (`gemini-2.5-flash`)
- **Orchestration**: LangChain

## How it works

1. Upload a PDF → text is extracted and split into chunks
2. Each chunk is embedded using Gemini and stored in ChromaDB
3. Ask a question → question is embedded → semantically similar chunks retrieved
4. Gemini answers using only the retrieved context (no hallucination)
