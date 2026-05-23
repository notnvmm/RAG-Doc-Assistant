# RAG Document Q&A Assistant

Ask natural language questions about any PDF document using Retrieval-Augmented Generation (RAG).

## Architecture
- **Frontend**: React.js + TypeScript
- **Backend**: FastAPI (Python)
- **Embeddings**: OpenAI text-embedding-ada-002
- **Vector Store**: ChromaDB
- **LLM**: GPT-3.5-turbo / GPT-4o
- **Orchestration**: LangChain

## How it works
1. Upload a PDF → text is extracted, chunked, embedded, stored in ChromaDB
2. Ask a question → question is embedded → similar chunks retrieved → GPT answers with context

## Setup
\```bash
# Backend
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your OpenAI API key
uvicorn main:app --reload

# Frontend  
cd frontend && npm install && npm start
\```

## Docker
\```bash
docker-compose up --build
\```