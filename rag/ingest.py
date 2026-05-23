from dotenv import load_dotenv
import os
import pickle
from io import BytesIO

import boto3
from pypdf import PdfReader

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv()

# -----------------------------
# AWS S3
# -----------------------------

S3_BUCKET = os.getenv("S3_BUCKET")
S3_PREFIX = os.getenv("S3_PREFIX", "documents/")

# -----------------------------
# Pinecone
# -----------------------------

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX", "enacton-rag")

# -----------------------------
# Local Storage
# -----------------------------

STORAGE_FOLDER = "storage"
os.makedirs(STORAGE_FOLDER, exist_ok=True)

# -----------------------------
# Embeddings
# -----------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2",
    model_kwargs={"device": "cpu"}
)

# -----------------------------
# Load PDFs From S3
# -----------------------------

s3 = boto3.client("s3")

documents = []

response = s3.list_objects_v2(
    Bucket=S3_BUCKET,
    Prefix=S3_PREFIX
)

for obj in response.get("Contents", []):

    key = obj["Key"]

    if not key.endswith(".pdf"):
        continue

    print(f"Loading: {key}")

    pdf_obj = s3.get_object(
        Bucket=S3_BUCKET,
        Key=key
    )

    pdf_bytes = pdf_obj["Body"].read()

    reader = PdfReader(
        BytesIO(pdf_bytes)
    )

    for page_num, page in enumerate(reader.pages):

        text = page.extract_text()

        if not text:
            continue

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": key,
                    "page": page_num + 1
                }
            )
        )

print(f"Loaded {len(documents)} pages from S3")

# -----------------------------
# Chunking
# -----------------------------

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_documents(documents)

# -----------------------------
# Save Chunks for BM25
# -----------------------------

with open(
    os.path.join(STORAGE_FOLDER, "chunks.pkl"),
    "wb"
) as f:
    pickle.dump(chunks, f)

print(f"Created {len(chunks)} chunks")

# -----------------------------
# Upload To Pinecone
# -----------------------------

print("Uploading to Pinecone...")

try:

    PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=INDEX_NAME
    )

    print(
        f"Successfully uploaded {len(chunks)} chunks to {INDEX_NAME}"
    )

except Exception as e:

    print(f"Pinecone Error: {e}")