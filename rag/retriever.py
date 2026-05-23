import os
import pickle
from dotenv import load_dotenv

from langchain_community.retrievers import BM25Retriever
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

# Optional
# from sentence_transformers import CrossEncoder

load_dotenv()

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
# EMBEDDINGS
# =========================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2",
    model_kwargs={"device": "cpu"}
)

# =========================
# BM25
# =========================

try:

    with open(chunks_path, "rb") as f:
        chunks = pickle.load(f)

    bm25_retriever = BM25Retriever.from_documents(
        chunks
    )

    bm25_retriever.k = 8

except FileNotFoundError:

    print(
        "chunks.pkl not found. Run ingest.py"
    )

    bm25_retriever = None

# =========================
# PINECONE
# =========================

vectorstore = PineconeVectorStore(
    index_name=INDEX_NAME,
    embedding=embeddings
)

dense_retriever = vectorstore.as_retriever(
    search_kwargs={
        "k": 8
    }
)

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

    dense_docs = dense_retriever.invoke(query)

    sparse_docs = []

    if bm25_retriever:
        sparse_docs = bm25_retriever.invoke(query)

    merged = []

    seen = set()

    for doc in dense_docs + sparse_docs:

        if doc.page_content not in seen:

            seen.add(
                doc.page_content
            )

            merged.append(doc)

    # =====================
    # RERANK
    # =====================

    if reranker:

        pairs = [
            [query, doc.page_content]
            for doc in merged
        ]

        scores = reranker.predict(
            pairs
        )

        ranked = sorted(
            zip(merged, scores),
            key=lambda x: x[1],
            reverse=True
        )

        merged = [
            doc
            for doc, score in ranked
        ]

    return merged[:5]