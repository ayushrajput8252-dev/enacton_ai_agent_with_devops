import os
import pickle
import logging
from dotenv import load_dotenv

from langchain_community.retrievers import BM25Retriever
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv()

logger = logging.getLogger(__name__)

# =========================
# CONFIG
# =========================

INDEX_NAME = os.getenv("PINECONE_INDEX")

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

chunks_path = os.path.join(
    BASE_DIR,
    "storage",
    "chunks.pkl"
)

# =========================
# LAZY LOADING
# =========================

_embeddings = None
_bm25_retriever = None
_dense_retriever = None


def get_embeddings():
    """Lazy load embeddings on first use"""
    global _embeddings
    
    if _embeddings is None:
        logger.info("Loading embeddings model (first use)...")
        try:
            _embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-mpnet-base-v2",
                model_kwargs={"device": "cpu"}
            )
            logger.info("Embeddings model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embeddings: {e}")
            raise
    
    return _embeddings


def get_bm25_retriever():
    """Lazy load BM25 retriever on first use"""
    global _bm25_retriever
    
    if _bm25_retriever is None:
        try:
            if os.path.exists(chunks_path):
                logger.info("Loading BM25 retriever from chunks...")
                with open(chunks_path, "rb") as f:
                    chunks = pickle.load(f)
                
                _bm25_retriever = BM25Retriever.from_documents(chunks)
                _bm25_retriever.k = 8
                logger.info(f"BM25 retriever loaded with {len(chunks)} chunks")
            else:
                logger.warning(f"chunks.pkl not found at {chunks_path}")
                _bm25_retriever = None
        except Exception as e:
            logger.error(f"Failed to load BM25 retriever: {e}")
            _bm25_retriever = None
    
    return _bm25_retriever


def get_dense_retriever():
    """Lazy load Pinecone dense retriever on first use"""
    global _dense_retriever
    
    if _dense_retriever is None:
        try:
            logger.info("Loading Pinecone dense retriever...")
            embeddings = get_embeddings()
            
            vectorstore = PineconeVectorStore(
                index_name=INDEX_NAME,
                embedding=embeddings
            )
            
            _dense_retriever = vectorstore.as_retriever(
                search_kwargs={"k": 8}
            )
            logger.info("Dense retriever loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load dense retriever: {e}")
            _dense_retriever = None
    
    return _dense_retriever

# =========================
# OPTIONAL RERANKER
# =========================

reranker = None

# reranker = CrossEncoder(
#     "BAAI/bge-reranker-base"
# )

# =========================
# RETRIEVE
# =========================

def retrieve_docs(query):
    """
    Retrieve documents using hybrid search (dense + sparse)
    
    Args:
        query: Search query
        
    Returns:
        list: Top 5 ranked documents
    """
    try:
        # Get dense retriever (Pinecone)
        dense_retriever = get_dense_retriever()
        
        if not dense_retriever:
            logger.warning("Dense retriever not available")
            dense_docs = []
        else:
            dense_docs = dense_retriever.invoke(query)
            logger.info(f"Dense search returned {len(dense_docs)} results")
        
        # Get sparse retriever (BM25)
        sparse_docs = []
        bm25_retriever = get_bm25_retriever()
        
        if bm25_retriever:
            sparse_docs = bm25_retriever.invoke(query)
            logger.info(f"Sparse search returned {len(sparse_docs)} results")
        else:
            logger.warning("BM25 retriever not available")
        
        # Merge and deduplicate
        merged = []
        seen = set()
        
        for doc in dense_docs + sparse_docs:
            if doc.page_content not in seen:
                seen.add(doc.page_content)
                merged.append(doc)
        
        logger.info(f"Merged {len(merged)} unique documents")
        
        # Return top 5
        result = merged[:5]
        logger.info(f"Returning top {len(result)} documents")
        
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving documents: {e}")
        return []