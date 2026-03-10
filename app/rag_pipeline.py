import chromadb
import ollama
from sentence_transformers import SentenceTransformer

# Location where the vector database will be stored
CHROMA_DIR = "chroma_db"
# Name of the Chroma collection
COLLECTION_NAME = "project1_docs"
TOP_K = 3

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect from Docker container to Ollama running on the Windows host
ollama_client = ollama.Client(host="http://host.docker.internal:11434")


def get_collection():
# Connect to the local ChromaDB vector database and return the document collection.
# If the collection does not already exist, it will be created automatically.
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    return collection


def retrieve_relevant_chunks(query, top_k=TOP_K):
# Convert the user query into an embedding vector and search the vector database.
# Returns the top matching document chunks based on semantic similarity.
    collection = get_collection()

    query_embedding = embedding_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results


def build_context(results):
# Combine the retrieved document chunks into a single context string.
# This context will later be passed to the LLM for answer generation.
# Also returns metadata for citation purposes.
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    context = "\n\n".join(documents)

    return context, metadatas


def generate_answer(query, context):
# Send the query and retrieved context to the local LLM (Ollama).
# The prompt instructs the model to answer using only the provided context
# to prevent hallucinated information.

    prompt = f"""
You are a helpful tabletop RPG assistant.

Answer the question using ONLY the provided context.

If the answer cannot be found in the context, say:
"I could not find that information in the documents."

Context:
{context}

Question:
{query}
"""

    response = ollama_client.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]


def format_citations(metadatas):
# Format the metadata from retrieved chunks into readable citations.
# Removes duplicates and lists the source file and page number.
    seen = set()
    citations = []

    for meta in metadatas:
        source = meta.get("source")
        page = meta.get("page")

        citation = f"{source} (page {page})"

        if citation not in seen:
            citations.append(citation)
            seen.add(citation)

    return "\n".join(citations)


def ask_rag(query):
# Main RAG pipeline function.
# Executes the full process: retrieve relevant chunks, build context,
# generate an answer with the LLM, and attach source citations.
    results = retrieve_relevant_chunks(query)

    context, metadatas = build_context(results)

    answer = generate_answer(query, context)

    citations = format_citations(metadatas)

    return f"{answer}\n\nSources:\n{citations}"