#!/usr/bin/env python3
"""
StartServer Script - Launch FastAPI backend and optionally Next.js frontend
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists(".env"):
        print_header("ERROR: .env file not found")
        print("Please create a .env file with required configuration:")
        print("  cp .env.example .env")
        print("  # Edit .env with your credentials")
        sys.exit(1)
    print_header("Environment Configuration")
    print("✓ .env file found")

def check_dependencies():
    """Check if required packages are installed"""
    print_header("Checking Dependencies")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "langchain",
        "pinecone",
        "sentence_transformers"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package}")
            missing.append(package)
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Install them with:")
        print(f"  pip install -r requirements.txt")
        response = input("\nInstall now? (y/n): ").strip().lower()
        if response == 'y':
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        else:
            sys.exit(1)

def test_pinecone():
    """Test Pinecone connection"""
    print_header("Testing Pinecone Connection")
    
    try:
        from pinecone import Pinecone
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        index = pc.Index(os.getenv('PINECONE_INDEX', 'enacton-rag'))
        stats = index.describe_index_stats()
        
        print(f"✓ Connected to Pinecone")
        print(f"  Index: {os.getenv('PINECONE_INDEX')}")
        print(f"  Total vectors: {stats.total_vector_count}")
        print(f"  Status: {'Ready' if stats.ready else 'Not Ready'}")
        
        if stats.total_vector_count == 0:
            print("\n⚠ WARNING: No vectors found in Pinecone!")
            print("Run document ingestion first:")
            print("  python ingest_documents.py")
            response = input("\nContinue anyway? (y/n): ").strip().lower()
            if response != 'y':
                sys.exit(1)
        
        return True
        
    except Exception as e:
        print(f"✗ Pinecone connection failed: {e}")
        print("\nMake sure:")
        print("  1. PINECONE_API_KEY is set in .env")
        print("  2. PINECONE_INDEX is set in .env")
        print("  3. Pinecone index exists in your account")
        response = input("\nContinue anyway? (y/n): ").strip().lower()
        return response == 'y'

def start_fastapi():
    """Start FastAPI server"""
    print_header("Starting FastAPI Backend")
    
    print("Starting on http://localhost:8000")
    print("Swagger UI: http://localhost:8000/docs")
    print("(Press Ctrl+C to stop)\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\nFastAPI server stopped")
        sys.exit(0)

def start_nextjs():
    """Start Next.js frontend"""
    print_header("Starting Next.js Frontend")
    
    print("Starting on http://localhost:3000")
    print("(Press Ctrl+C to stop)\n")
    
    try:
        subprocess.run(["npm", "run", "dev"])
    except KeyboardInterrupt:
        print("\nNext.js server stopped")
        sys.exit(0)

def main():
    """Main entry point"""
    
    print_header("EnactOn AI RAG Chatbot - Startup")
    
    # Check environment
    check_env_file()
    check_dependencies()
    test_pinecone()
    
    # Ask what to start
    print_header("Select What to Start")
    print("1. FastAPI Backend only (default)")
    print("2. Next.js Frontend only")
    print("3. Both (requires 2 terminal windows)")
    print("4. Show setup instructions")
    print("5. Run document ingestion")
    
    choice = input("\nEnter choice (1-5) [1]: ").strip() or "1"
    
    if choice == "1":
        start_fastapi()
    elif choice == "2":
        start_nextjs()
    elif choice == "3":
        print("\nTo run both servers:")
        print("\n  Terminal 1 (Backend):")
        print("    python main.py")
        print("\n  Terminal 2 (Frontend):")
        print("    npm run dev")
        print("\n  Frontend: http://localhost:3000")
        print("  Backend: http://localhost:8000")
        print("  Swagger: http://localhost:8000/docs")
        sys.exit(0)
    elif choice == "4":
        print("\nRefer to SETUP_GUIDE.md for complete instructions:")
        print("  • Installation steps")
        print("  • Environment configuration")
        print("  • Running the application")
        print("  • Document ingestion")
        print("  • Troubleshooting")
        print("  • Deployment options")
        sys.exit(0)
    elif choice == "5":
        print("\nStarting document ingestion...\n")
        subprocess.run([sys.executable, "ingest_documents.py"])
        sys.exit(0)
    else:
        print("Invalid choice")
        sys.exit(1)

if __name__ == "__main__":
    main()
