import os
import fitz  # PyMuPDF
import google.generativeai as genai
import hashlib

from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from dotenv import load_dotenv
load_dotenv()
# Set up Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
# Custom embedding function using Gemini text embedding mode
from chromadb.utils.embedding_functions import GoogleGenerativeAiEmbeddingFunction
import chromadb.utils.embedding_functions as embedding_functions

# Use ChromaDB's built-in Gemini embedding function
embedding_function = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
    api_key=GEMINI_API_KEY
)

def process_pdf(file_path: str, username: str, chroma_client):
    """
    Extracts text from PDF, chunks it, and stores Gemini embeddings in ChromaDB
    """
    with fitz.open(file_path) as doc:
        texts = [page.get_text() for page in doc]

    full_text = "\n".join(texts)
    chunks = [full_text[i:i + 1000] for i in range(0, len(full_text), 1000)]

    collection = chroma_client.get_or_create_collection(
        name=f"user_{username}",
        embedding_function=embedding_function
    )

    collection.add(
        documents=chunks,
        metadatas=[{"source": os.path.basename(file_path)} for _ in chunks],
        ids=[f"{os.path.basename(file_path)}_{i}" for i in range(len(chunks))]
    )


def query_llm(username: str, query: str, chroma_client) -> str:
    """
    Uses Chroma to retrieve context, then sends question to Gemini Pro
    """
    collection = chroma_client.get_or_create_collection(
        name=f"user_{username}",
        embedding_function=embedding_function
    )

    results = collection.query(query_texts=[query], n_results=3)

    documents = results["documents"][0] if results["documents"] else []
    context = "\n\n".join(documents)

    prompt = f"You are a helpful assistant. Use the context below to answer the question.\n\nContext:\n{context}\n\nQuestion: {query}"

    model = genai.GenerativeModel("gemini-1.5-pro-002")
    response = model.generate_content(prompt)

    return response.text.strip()