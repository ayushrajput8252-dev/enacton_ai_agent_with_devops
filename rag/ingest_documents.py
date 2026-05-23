#!/usr/bin/env python3
"""
Document Ingestion Script for EnactOn AI RAG
Ingests the local company PDF into Pinecone
"""

import os
import sys
import logging
import pickle
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# ============================
# IMPORTS
# ============================

try:
    from pypdf import PdfReader
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_pinecone import PineconeVectorStore
    from pinecone import Pinecone
    
    logger.info("All dependencies imported successfully")
except ImportError as e:
    logger.error(f"Failed to import dependencies: {e}")
    logger.error("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)

# ============================
# CONFIGURATION
# ============================

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX", "enacton-rag")

# Local PDF source
PDF_PATH = Path(os.getenv("LOCAL_PDF_PATH", "company.pdf"))

# Storage
STORAGE_FOLDER = "rag/storage"
os.makedirs(STORAGE_FOLDER, exist_ok=True)

chunks_path = os.path.join(STORAGE_FOLDER, "chunks.pkl")

# ============================
# EMBEDDINGS
# ============================

logger.info("Loading embeddings model...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2",
    model_kwargs={"device": "cpu"}
)
logger.info("Embeddings model loaded")

# ============================
# TEXT SPLITTER
# ============================

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

# ============================
# DOCUMENT LOADING FUNCTIONS
# ============================

def load_company_pdf(pdf_path: Path) -> list:
    """Load pages from the local company PDF."""
    documents = []
    
    if not pdf_path.exists():
        logger.error(f"PDF not found: {pdf_path.resolve()}")
        return documents
    
    logger.info(f"Loading local PDF: {pdf_path.resolve()}")

    try:
        reader = PdfReader(str(pdf_path))

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()

            if text and text.strip():
                documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "source": pdf_path.name,
                            "page": page_num + 1
                        }
                    )
                )

        logger.info(f"Loaded {len(documents)} text pages from {pdf_path.name}")
        
    except Exception as e:
        logger.error(f"Error loading {pdf_path.name}: {e}")
    
    return documents


# ============================
# MAIN INGESTION FLOW
# ============================

def ingest_documents():
    """Main function to ingest documents into Pinecone"""
    
    logger.info("=" * 60)
    logger.info("Starting Document Ingestion")
    logger.info("=" * 60)
    
    logger.info("\n1. Loading company PDF...")
    all_documents = load_company_pdf(PDF_PATH)
    logger.info(f"   Loaded {len(all_documents)} pages from {PDF_PATH}")

    if not all_documents:
        logger.error("No text could be extracted from the company PDF")
        sys.exit(1)
    
    # ============================
    # CHUNKING
    # ============================
    
    logger.info("\n2. Chunking documents...")
    chunks = splitter.split_documents(all_documents)
    logger.info(f"   Created {len(chunks)} chunks from {len(all_documents)} documents")
    
    # ============================
    # SAVE CHUNKS FOR BM25
    # ============================
    
    logger.info("\n3. Saving chunks for BM25 retrieval...")
    try:
        with open(chunks_path, "wb") as f:
            pickle.dump(chunks, f)
        logger.info(f"   Chunks saved to {chunks_path}")
    except Exception as e:
        logger.error(f"   Failed to save chunks: {e}")
    
    # ============================
    # UPLOAD TO PINECONE
    # ============================
    
    logger.info("\n4. Replacing Pinecone vectors...")
    logger.info(f"   Index: {INDEX_NAME}")
    logger.info(f"   Total vectors: {len(chunks)}")
    
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(INDEX_NAME)
        index.delete(delete_all=True)
        logger.info("   Existing Pinecone vectors deleted")
        
        PineconeVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
            index_name=INDEX_NAME
        )
        
        logger.info(f"   Successfully uploaded {len(chunks)} chunks to {INDEX_NAME}")
        
    except Exception as e:
        logger.error(f"   Pinecone Error: {e}")
        logger.error("   Make sure PINECONE_API_KEY and PINECONE_INDEX are set")
        sys.exit(1)
    
    logger.info("\n" + "=" * 60)
    logger.info("Document Ingestion Complete!")
    logger.info("=" * 60)
    
    return {
        "success": True,
        "total_documents": len(all_documents),
        "total_chunks": len(chunks),
        "index": INDEX_NAME
    }


# ============================
# VERIFICATION
# ============================

def verify_pinecone():
    """Verify Pinecone setup after ingestion"""
    
    logger.info("\nVerifying Pinecone setup...")
    
    try:
        from pinecone import Pinecone
        
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(INDEX_NAME)
        stats = index.describe_index_stats()
        
        logger.info(f"  Index: {INDEX_NAME}")
        logger.info(f"  Total vectors: {stats.total_vector_count}")
        logger.info(f"  Status: {'Ready' if stats.ready else 'Not Ready'}")
        
        return stats.total_vector_count > 0
        
    except Exception as e:
        logger.error(f"  Verification failed: {e}")
        return False


# ============================
# CLI
# ============================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Ingest documents into Pinecone for RAG"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Only verify Pinecone setup without ingesting"
    )
    
    args = parser.parse_args()
    
    if args.verify:
        if verify_pinecone():
            logger.info("Pinecone is ready!")
            sys.exit(0)
        else:
            logger.error("Pinecone is not ready. Run ingestion first.")
            sys.exit(1)
    else:
        result = ingest_documents()
        
        if verify_pinecone():
            logger.info("Verification successful!")
            sys.exit(0)
        else:
            logger.error("Verification failed!")
            sys.exit(1)
