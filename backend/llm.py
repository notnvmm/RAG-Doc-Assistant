from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import Document
import os
from dotenv import load_dotenv

load_dotenv()


def build_prompt(question: str, context_chunks: list[Document]) -> str:
    context_text = "\n\n---\n\n".join([doc.page_content for doc in context_chunks])

    return f"""You are a helpful assistant that answers questions based ONLY on the provided document context.

Rules:
- Answer ONLY using the context below. Do not use outside knowledge.
- If the answer is not in the context, say: "I couldn't find this information in the document."
- Be concise and direct.

CONTEXT FROM DOCUMENT:
{context_text}

QUESTION: {question}

ANSWER:"""


def get_llm_answer(question: str, context_chunks: list[Document]) -> dict:
    if not context_chunks:
        return {
            "answer": "No relevant content found in the document.",
            "sources": []
        }

    prompt = build_prompt(question, context_chunks)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.1
    )

    response = llm.invoke(prompt)

    sources = [
        {
            "page": doc.metadata.get("page", "unknown"),
            "snippet": doc.page_content[:150] + "..."
        }
        for doc in context_chunks
    ]

    return {
        "answer": response.content,
        "sources": sources
    }