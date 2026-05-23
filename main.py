"""
FastAPI Backend for EnactOn AI RAG Chatbot
Bridges the Next.js frontend with Python RAG backend
"""

import os
import logging
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag.rag_agent import rag_agent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================
# MODELS
# ============================

class ChatMessage(BaseModel):
    """Chat message request model"""
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    session_id: str = "default"


# ============================
# LIFESPAN EVENTS
# ============================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events for the FastAPI application
    """
    # Startup
    logger.info("FastAPI server starting...")
    logger.info(f"Pinecone Index: {os.getenv('PINECONE_INDEX')}")
    logger.info(f"GROQ Model: {os.getenv('GROQ_MODEL')}")
    
    yield
    
    # Shutdown
    logger.info("FastAPI server shutting down...")


# ============================
# CREATE APP
# ============================

app = FastAPI(
    title="EnactOn AI RAG Backend",
    description="FastAPI backend for RAG-powered chatbot",
    version="1.0.0",
    lifespan=lifespan
)

# ============================
# CORS CONFIGURATION
# ============================

origins = [
    "http://localhost:3000",      # Next.js dev server
    "http://localhost:8000",      # FastAPI dev server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://localhost",
    "*",  # Allow all for development (restrict in production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================
# HEALTH CHECK ENDPOINT
# ============================

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify server is running
    """
    return {
        "status": "healthy",
        "service": "EnactOn AI RAG Backend"
    }


@app.get("/config")
async def get_config():
    """
    Get current configuration (non-sensitive)
    """
    return {
        "pinecone_index": os.getenv("PINECONE_INDEX"),
        "groq_model": os.getenv("GROQ_MODEL"),
        "embedding_model": "sentence-transformers/all-mpnet-base-v2",
    }


# ============================
# CHAT ENDPOINT - NON-STREAMING
# ============================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatMessage):
    """
    Chat endpoint that uses RAG to answer questions
    
    Args:
        request: ChatMessage with user query
        
    Returns:
        ChatResponse with assistant's answer
        
    Raises:
        HTTPException: If RAG agent fails
    """
    try:
        logger.info(f"Chat request received - Session: {request.session_id}")
        logger.debug(f"User message: {request.message}")
        
        # Call RAG agent
        response = rag_agent(
            query=request.message,
            session_id=request.session_id
        )
        
        logger.info(f"Response generated - Length: {len(response)}")
        
        return ChatResponse(
            response=response,
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )


# ============================
# CHAT ENDPOINT - STREAMING
# ============================

async def stream_response(query: str, session_id: str) -> AsyncGenerator[str, None]:
    """
    Generator that streams the RAG response word by word
    
    Args:
        query: User's question
        session_id: Session identifier
        
    Yields:
        Response chunks
    """
    try:
        logger.info(f"Streaming chat request - Session: {session_id}")
        logger.debug(f"User message: {query}")
        
        # Get response from RAG agent
        response = rag_agent(
            query=query,
            session_id=session_id
        )
        
        # Stream response word by word
        words = response.split()
        for word in words:
            yield word + " "
            
        logger.info(f"Stream completed - Length: {len(response)}")
        
    except Exception as e:
        logger.error(f"Error in streaming: {type(e).__name__}: {str(e)}")
        yield f"Error: {str(e)}"


@app.post("/api/chat/stream")
async def chat_stream(request: ChatMessage):
    """
    Streaming chat endpoint that returns response word-by-word
    
    Args:
        request: ChatMessage with user query
        
    Returns:
        StreamingResponse with text/plain content
    """
    return StreamingResponse(
        stream_response(request.message, request.session_id),
        media_type="text/plain; charset=utf-8"
    )


# ============================
# ERROR HANDLERS
# ============================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled Exception: {type(exc).__name__}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500
        }
    )


# ============================
# DEBUG ENDPOINTS (DEVELOPMENT ONLY)
# ============================

@app.post("/api/debug/test-rag")
async def test_rag(request: ChatMessage):
    """
    Test RAG agent directly (development only)
    """
    try:
        logger.info(f"Testing RAG agent with query: {request.message}")
        
        response = rag_agent(
            query=request.message,
            session_id=request.session_id
        )
        
        return {
            "success": True,
            "query": request.message,
            "response": response
        }
        
    except Exception as e:
        logger.error(f"RAG test failed: {type(e).__name__}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "query": request.message
        }


# ============================
# ROOT ENDPOINT
# ============================

@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return {
        "service": "EnactOn AI RAG Backend",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "config": "GET /config",
            "chat": "POST /api/chat",
            "chat_stream": "POST /api/chat/stream",
            "test_rag": "POST /api/debug/test-rag"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
