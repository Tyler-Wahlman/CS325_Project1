# CS325_Project1 - Retrieval Augmented Generation (RAG) Assistant

## Overview

This project implements a Retrieval-Augmented Generation (RAG) system that answers questions using information from a collection of RPG rulebooks and lore documents. The system ingests documents, converts them into embeddings, stores them in a vector database, retrieves relevant information for a user query, and generates a response using a local Large Language Model (LLM).

The assistant supports PDF, DOCX, and TXT documents and runs entirely locally using Docker and Ollama.

---

## Features

- Supports PDF, DOCX, and TXT document ingestion
- Automatic text chunking
- Semantic embeddings using SentenceTransformers
- Vector storage using ChromaDB
- Local LLM generation using Ollama (Llama3)
- Source citation for answers
- Simple command line interface
- Fully containerized with Docker

---

## RAG Pipeline Architecture

The system follows a typical Retrieval-Augmented Generation pipeline:


Documents
|
Document Parsing
|
Text Chunking
|
Embedding Generation
|
Vector Storage (ChromaDB)
|
Query Embedding
|
Similarity Search
|
Retrieve Context
|
LLM Generation (Ollama)
|
CLI Response


---

## Technologies Used

| Component | Technology |
|--------|--------|
| Programming Language | Python 3.11 |
| Embedding Model | SentenceTransformers (`all-MiniLM-L6-v2`) |
| Vector Database | ChromaDB |
| Local LLM | Ollama (`llama3`) |
| Document Parsing | PyPDF2, python-docx |
| Containerization | Docker |

---

## Document Ingestion

The ingestion system loads documents from the `data` folder.

Supported formats:

| Format | Parser |
|------|------|
| PDF | PyPDF2 |
| DOCX | python-docx |
| TXT | Python file reader |

Documents are processed through the following steps:

1. Extract raw text
2. Clean formatting and whitespace
3. Split text into chunks
4. Generate embeddings
5. Store vectors and metadata in ChromaDB

---

## Chunking Strategy

Documents are split into smaller overlapping chunks to improve retrieval accuracy.


Chunk Size: 100 words
Chunk Overlap: 20 words


Example:


Chunk 1 - words 1-100
Chunk 2 - words 81-180
Chunk 3 - words 161-260


Overlap preserves context between adjacent chunks.

---

## Embedding Model

The system uses the SentenceTransformers model:


all-MiniLM-L6-v2


This model was selected because it:

- Produces high-quality semantic embeddings
- Is lightweight and efficient
- Runs locally without requiring an API

Embeddings convert text into numerical vectors that allow semantic similarity search.

---

## Vector Database

ChromaDB is used as the vector store.

Each stored entry contains:

- Chunk text
- Embedding vector
- Source document
- Page number
- Chunk index

Similarity search is performed using cosine similarity between query and stored vectors.

---

## Retrieval Process

When a user asks a question:

1. The question is converted into an embedding.
2. ChromaDB searches for the most similar document chunks.
3. The top results are retrieved.
4. These chunks form the context passed to the LLM.

---

## Generation with Ollama

Answer generation is handled by a local LLM using Ollama.

Model used:


llama3


The prompt instructs the model to answer only using the retrieved context to prevent hallucinated responses.

Example prompt:


Answer the question using ONLY the provided context.

Context:
<retrieved document chunks>

Question:
<user question>


---

## Running the Project

### 1. Install Ollama

Download Ollama from:


https://ollama.com/download


Then pull the model:


ollama pull llama3


---

### 2. Build the Docker container


docker build -t project1 .


---

### 3. Run the container


docker run -it --rm project1


The assistant will start and prompt for questions.

---

## Example Queries


What regions exist in Eldoria?

What abilities does a Stone Troll have?

What types of magic exist?

What armor can adventurers use?


Example output:


Answer:
The major regions of Eldoria include Silverwood Forest, Ironpeak Mountains,
and the Storm Coast.

Sources:
world_lore.pdf (page 1)


---

## Preventing Hallucinations

The prompt used for generation requires the model to answer only from retrieved context. If the information cannot be found in the documents, the assistant responds:


I could not find that information in the documents.


This ensures grounded responses.

---

## Future Improvements

Potential enhancements include:

- Web interface (Flask or FastAPI)
- Hybrid search (vector + keyword)
- Improved ranking of retrieved chunks
- Metadata filtering
- Multi-query retrieval
- Larger embedding models

---

## Author

CS325 - Project 1  
Tyler Wahlman
Retrieval-Augmented Generation Assistant