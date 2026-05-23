#!/usr/bin/env python3
"""
Check Pinecone connection and embeddings
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    from pinecone import Pinecone
    print("✓ Pinecone package installed")
except ImportError:
    print("✗ Pinecone package NOT installed")
    sys.exit(1)

try:
    pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    index = pc.Index(os.getenv('PINECONE_INDEX', 'enacton-rag'))
    stats = index.describe_index_stats()
    
    print(f"\n✓ Connected to Pinecone")
    print(f"  Index: {os.getenv('PINECONE_INDEX')}")
    print(f"  Total vectors: {stats.total_vector_count}")
    print(f"  Index ready: {stats.ready}")
    print(f"  Namespace count: {len(stats.namespaces)}")
    
except Exception as e:
    print(f"\n✗ Error connecting to Pinecone: {e}")
    sys.exit(1)

print("\n✓ Setup looks good!")
