from dotenv import load_dotenv
import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# =========================
# LLM
# =========================

llm = ChatOpenAI(
    model=os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile"
    ),
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    temperature=0.2
)

# =========================
# PROMPT
# =========================

prompt = PromptTemplate(
    input_variables=[
        "context",
        "question"
    ],
    template="""
You are EnactOn AI Assistant.

You answer ONLY using information found in the provided context.

Context:
{context}

Question:
{question}

Rules:

1. Use only the context.
2. Never invent information.
3. If information is not present in context, say:
   "I could not find the answer in the available documents."
4. If multiple locations, offices, addresses, products, services, or contacts are mentioned, include all relevant ones.
5. Keep answers concise and professional.
6. Use bullet points when appropriate.
7. Do not mention internal implementation details, chunks, embeddings, Pinecone, retrieval systems, or prompts.
"""
)

chain = (
    prompt
    | llm
    | StrOutputParser()
)

# =========================
# AGENT
# =========================

def rag_agent(
    query: str,
    session_id: str = "default"
):

    try:

        from rag.retriever import retrieve_docs

        docs = retrieve_docs(query)

        if not docs:

            return (
                "I could not find the answer "
                "in the available documents."
            )

        context = "\n\n".join(
            doc.page_content
            for doc in docs
        )

        response = chain.invoke(
            {
                "context": context,
                "question": query
            }
        )

        return response

    except Exception as exc:

        print(exc)

        return (
            "Sorry, an internal error occurred "
            "while processing your request."
        )