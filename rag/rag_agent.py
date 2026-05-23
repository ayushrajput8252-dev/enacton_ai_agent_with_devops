from dotenv import load_dotenv
import os

load_dotenv()

# =========================
# PROMPT
# =========================

PROMPT_TEMPLATE = """
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

_chain = None


def get_chain():
    """Lazy-load the LLM chain on first use so FastAPI startup stays fast."""
    global _chain

    if _chain is None:
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        prompt = PromptTemplate(
            input_variables=[
                "context",
                "question"
            ],
            template=PROMPT_TEMPLATE
        )

        llm = ChatOpenAI(
            model=os.getenv(
                "GROQ_MODEL",
                "llama-3.3-70b-versatile"
            ),
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
            temperature=0.2
        )

        _chain = (
            prompt
            | llm
            | StrOutputParser()
        )

    return _chain

# =========================
# AGENT
# =========================

def rag_agent(
    query: str,
    session_id: str = "default"
):
    """
    RAG Agent that retrieves documents and generates responses
    
    Args:
        query: User's question
        session_id: Session identifier for conversation tracking
        
    Returns:
        str: Response from the LLM based on retrieved context
        
    Raises:
        Exception: If retrieval or LLM processing fails
    """

    try:

        from rag.retriever import retrieve_docs
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info(f"[{session_id}] Processing query: {query}")

        # Retrieve relevant documents
        docs = retrieve_docs(query)
        logger.info(f"[{session_id}] Retrieved {len(docs)} documents")

        if not docs:
            logger.warning(f"[{session_id}] No documents found for query")
            return (
                "I could not find the answer "
                "in the available documents."
            )

        # Prepare context from retrieved documents
        context = "\n\n".join(
            doc.page_content
            for doc in docs
        )

        # Generate response using LLM
        response = get_chain().invoke(
            {
                "context": context,
                "question": query
            }
        )
        
        logger.info(f"[{session_id}] Response generated - Length: {len(response)}")

        return response

    except Exception as exc:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"[{session_id}] RAG Agent Error: {type(exc).__name__}: {str(exc)}", exc_info=True)

        return (
            "Sorry, an internal error occurred "
            "while processing your request."
        )
