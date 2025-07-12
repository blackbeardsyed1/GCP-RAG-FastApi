# 🚀 AI-Powered PDF Chat Backend (RAG) using FastAPI + GCP + Gemini/OpenAI

A robust, production-ready **Retrieval-Augmented Generation (RAG)** backend built with **FastAPI**, **ChromaDB**, and **Gemini/OpenAI LLMs** — deployed on **Google Cloud Platform (GCP)** with secure, programmatic user access.

> ⚡️ 100+ requests/min | 🔐 User authentication | 📄 PDF document-based Q&A | ☁️ GCP Persistent Storage | 🧠 Embedding with Gemini

---


---

## ✨ Features

- ✅ **FastAPI Backend** — Lightweight, performant, RESTful API
- 🔐 **User Authentication** — Each user has their own password & access scope
- 📄 **Per-user PDF Uploads** — Isolated document store for each user
- 🔎 **Document Indexing & Embedding** — Uses Gemini embeddings & ChromaDB
- 🤖 **LLM Querying** — Contextual Q&A powered by Gemini or OpenAI
- 💬 **Parallel Conversations** — Supports 30+ users, 100 requests/min tested
- 📁 **Persistent GCP Storage** — Stores PDFs, chat history, and embeddings on external disk
- 🧪 **Load Testing** — Includes Python-based local simulation for concurrency testing
- 🛠️ **Admin Console** — Python CLI to manage users & documents securely

---

## 🧠 RAG Architecture Overview

1. **User uploads PDF**
2. **PDF is chunked + embedded (Gemini)**
3. **Chunks stored in ChromaDB**
4. **User sends a question**
5. **ChromaDB retrieves relevant context**
6. **Gemini LLM generates response**

---

## 🛠️ Tech Stack

| Tool        | Role                         |
|-------------|------------------------------|
| FastAPI     | Backend API Server           |
| ChromaDB    | Vector DB for document search|
| Gemini/OpenAI | Large Language Model (LLM)  |
| PyMuPDF     | PDF text extraction          |
| aiohttp     | Async load testing           |
| GCP VM + Disk | Deployment + Persistent Storage |

---

## 📂 Project Structure

FastApi-GCP-Rag/
├── main.py # FastAPI app
├── rag_engine.py # Embedding + LLM logic
├── chroma_client/ # ChromaDB storage
├── users/ # Per-user folders
│ └── <username>/pdfs/ # User PDFs
├── client.py # Python admin CLI (upload/query/delete)
├── load_test.py # Async load testing script
├── users.json # Local user registry
├── requirements.txt
└── README.md


---

## ⚙️ Setup Instructions

### 🔧 1. GCP VM Setup
- Create a GCP VM (Ubuntu 22+)
- Attach a persistent disk and mount it
- Install dependencies:
```bash
sudo apt update
sudo apt install python3-pip git unzip
pip install -r requirements.txt
```
### 🔑 2. Environment Configuration
Create a .env file:
GEMINI_API_KEY=your_gemini_key_here

### 🚀 3. Run FastAPI App

uvicorn main:app --host 0.0.0.0 --port 8000

### 🖥️ 4.Local Admin Client
Use client.py for managing users & testing PDF queries.

python client.py

Features:

✅ Create/Delete users

📁 Upload/List/Delete PDFs

💬 Ask questions on uploaded PDFs

📚 View user list

🔐 Auto-updates users.json based on backend state

### 🧪 Load Testing
Test scalability with:
python load_test.py --users 30 --queries 4 --input users.json
This will simulate:

30 parallel users

4 queries each

100+ requests/minute

### ❗ Common Errors & Fixes
Error	Fix
models/gemini-pro not found	Ensure you're using correct Gemini model name (e.g., gemini-1.5-pro-002)
users.json not found	Automatically created by client.py or add manually
invalid SSH key format on Windows	Convert PEM to OpenSSH with PuTTYgen or use correct .ppk
ChromaDB folder missing	Ensure path exists and is mounted correctly
