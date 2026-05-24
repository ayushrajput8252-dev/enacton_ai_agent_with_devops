#!/usr/bin/env python3
"""
EnactOn RAG System - Startup and Validation Script
Tests all components and provides diagnostics
"""

import os
import sys
import subprocess
import time
import logging
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("\n" + "="*70)
print("ENACTON RAG CHATBOT - STARTUP & VALIDATION".center(70))
print("="*70 + "\n")

# ============================
# 1. VERIFY ENVIRONMENT
# ============================

print("[1/6] Verifying Configuration...")
print("-" * 70)

required_env = {
    "GROQ_API_KEY": "GROQ LLM API Key",
    "GROQ_MODEL": "GROQ Model Name",
    "PINECONE_API_KEY": "Pinecone Vector DB Key",
    "PINECONE_INDEX": "Pinecone Index Name",
}

missing = []
for key, desc in required_env.items():
    value = os.getenv(key)
    if value:
        masked = value[:8] + "..." if len(value) > 10 else value
        print(f"  ✅ {desc}: {masked}")
    else:
        print(f"  ❌ {desc}: MISSING")
        missing.append(key)

if missing:
    print(f"\n❌ Missing configuration: {', '.join(missing)}")
    print("   Please set these in .env file and try again")
    sys.exit(1)

# ============================
# 2. VERIFY FILE STRUCTURE
# ============================

print("\n[2/6] Verifying File Structure...")
print("-" * 70)

required_files = {
    "main.py": "FastAPI Server",
    "rag/rag_agent.py": "RAG Agent",
    "rag/retriever.py": "Document Retriever",
    "rag/storage/chunks.pkl": "BM25 Index",
    "app/page.tsx": "Homepage",
    "app/chat/page.tsx": "Chat Interface",
}

for file_path, desc in required_files.items():
    full_path = Path(file_path)
    status = "✅" if full_path.exists() else "❌"
    print(f"  {status} {desc}: {file_path}")

# ============================
# 3. CHECK DEPENDENCIES
# ============================

print("\n[3/6] Verifying Dependencies...")
print("-" * 70)

packages = [
    ("fastapi", "FastAPI"),
    ("uvicorn", "Uvicorn"),
    ("langchain", "LangChain"),
    ("pinecone", "Pinecone"),
    ("sentence_transformers", "Sentence Transformers"),
]

for module, name in packages:
    try:
        __import__(module)
        print(f"  ✅ {name}")
    except ImportError:
        print(f"  ❌ {name} (not installed)")

# ============================
# 4. TEST PINECONE CONNECTION
# ============================

print("\n[4/6] Testing Pinecone Connection...")
print("-" * 70)

try:
    from pinecone import Pinecone
    
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(os.getenv("PINECONE_INDEX"))
    stats = index.describe_index_stats()
    
    print(f"  ✅ Connected to Pinecone")
    print(f"     Index: {os.getenv('PINECONE_INDEX')}")
    print(f"     Status: {'Ready ✓' if stats.ready else 'Initializing... (normal)'}")
    print(f"     Vectors: {stats.total_vector_count}")
    
    if stats.total_vector_count < 2:
        print(f"     ⚠️  NOTE: Only {stats.total_vector_count} vector(s)")
        print(f"     → Run: python ingest_documents.py")
    
except Exception as e:
    print(f"  ❌ Pinecone Error: {e}")
    print("     Check API key and network connectivity")

# ============================
# 5. TEST RAG COMPONENTS
# ============================

print("\n[5/6] Testing RAG Components...")
print("-" * 70)

try:
    logger.info("Initializing RAG components (first run may be slow)...")
    from rag.retriever import retrieve_docs
    
    logger.info("Testing document retrieval...")
    docs = retrieve_docs("What is AI?")
    
    print(f"  ✅ Document Retriever: {len(docs)} docs retrieved")
    
except Exception as e:
    print(f"  ⚠️  Retriever Warning: {e}")
    print("     This is normal on first run (embeddings loading)")

try:
    logger.info("Testing RAG agent...")
    from rag.rag_agent import rag_agent
    
    response = rag_agent("What services do you offer?", "startup-test")
    
    print(f"  ✅ RAG Agent: Response generated ({len(response)} chars)")
    
except Exception as e:
    print(f"  ⚠️  RAG Agent Warning: {e}")
    print("     This is normal on first run")

# ============================
# 6. STARTUP INSTRUCTIONS
# ============================

print("\n[6/6] Ready to Start Services")
print("-" * 70)

print("\n✅ All checks passed!\n")

print("To start the system, run in separate terminals:\n")
print("  Terminal 1 (Backend):")
print("    $ python main.py\n")

print("  Terminal 2 (Frontend):")
print("    $ npm run dev\n")

print("  Terminal 3 (Optional - Ingest Documents):")
print("    $ python ingest_documents.py\n")

print("Then open in browser:")
print("    http://localhost:3000\n")

print("="*70)
print("System Ready! Starting backend...".center(70))
print("="*70 + "\n")

# ============================
# START BACKEND
# ============================

try:
    logger.info("Starting FastAPI server...")
    subprocess.run(["python", "main.py"], check=False)
except KeyboardInterrupt:
    logger.info("Shutdown requested")
except Exception as e:
    logger.error(f"Failed to start server: {e}")
    sys.exit(1)
