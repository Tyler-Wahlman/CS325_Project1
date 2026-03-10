import os
from pathlib import Path
from typing import List, Dict

import chromadb
from PyPDF2 import PdfReader
from docx import Document
from sentence_transformers import SentenceTransformer

# Folder containing input documents
DATA_DIR = Path("data")
# Location where the vector database will be stored
CHROMA_DIR = "chroma_db"
# Name of the Chroma collection
COLLECTION_NAME = "project1_docs"

# Each chunk will contain ~100 words with a 20 word overlap
CHUNK_SIZE = 100 
CHUNK_OVERLAP = 20 

# Load HuggingFace as embedding model to convert text into vectors
embedding_model = SentenceTransformer("all-MiniLM-L6-v2") 


def read_pdf(file_path: Path) -> List[Dict]:        
# Read text from a PDF file
    pages_data = []
    reader = PdfReader(str(file_path))

    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = clean_text(text)

        if text.strip():
            pages_data.append(
                {
                    "text": text,
                    "source": file_path.name,
                    "page": page_num,
                    "file_type": "pdf",
                }
            )

    return pages_data


def read_docx(file_path: Path) -> List[Dict]:       
# Read text from a .docx file
    doc = Document(str(file_path))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    full_text = "\n".join(paragraphs)
    full_text = clean_text(full_text)

    if not full_text.strip():
        return []

    return [
        {
            "text": full_text,
            "source": file_path.name,
            "page": 1,
            "file_type": "docx",
        }
    ]


def read_txt(file_path: Path) -> List[Dict]:        
# Read text from a .txt file
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    text = clean_text(text)

    if not text.strip():
        return []

    return [
        {
            "text": text,
            "source": file_path.name,
            "page": 1,
            "file_type": "txt",
        }
    ]


def clean_text(text: str) -> str:
# Remove extra whitespace and normalize text
    return " ".join(text.split())


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:    
# Split document text into smaller overlapping chunks
    words = text.split()
    chunks = []

    if not words:
        return chunks

    step = chunk_size - overlap
    for i in range(0, len(words), step):
        chunk_words = words[i:i + chunk_size]
        chunk = " ".join(chunk_words).strip()
        if chunk:
            chunks.append(chunk)

    return chunks


def load_documents(data_dir: Path = DATA_DIR) -> List[Dict]:        
# Load all supported documents from the data folder
    documents = []

    if not data_dir.exists():
        raise FileNotFoundError(f"Data folder not found: {data_dir}")

    for file_path in data_dir.iterdir():
        if file_path.suffix.lower() == ".pdf":
            documents.extend(read_pdf(file_path))

        elif file_path.suffix.lower() == ".docx":
            documents.extend(read_docx(file_path))

        elif file_path.suffix.lower() == ".txt":
            documents.extend(read_txt(file_path))

    return documents


def build_chunks(documents: List[Dict]) -> List[Dict]:      
# Convert loaded documents into smaller chunks with metadata
    chunked_docs = []

    for doc in documents:
        chunks = chunk_text(doc["text"])

        for idx, chunk in enumerate(chunks):
            chunked_docs.append(
                {
                    "id": f"{doc['source']}_{doc['page']}_{idx}",
                    "text": chunk,
                    "metadata": {
                        "source": doc["source"],
                        "page": doc["page"],
                        "chunk_index": idx,
                        "file_type": doc["file_type"],
                    },
                }
            )

    return chunked_docs


def create_vector_store(chunked_docs: List[Dict]) -> None:          
# Store chunks and embeddings inside ChromaDB
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    ids = [doc["id"] for doc in chunked_docs]
    texts = [doc["text"] for doc in chunked_docs]
    metadatas = [doc["metadata"] for doc in chunked_docs]

    embeddings = embedding_model.encode(texts).tolist()

    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings,
    )



def build_index_if_needed() -> None:    
# Run the full ingestion process if the vector database does not exist
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    existing = collection.get()

    documents = load_documents()

    chunked_docs = build_chunks(documents)

    create_vector_store(chunked_docs)


if __name__ == "__main__":
    build_index_if_needed()