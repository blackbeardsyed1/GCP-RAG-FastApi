# main.py
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import shutil
from dotenv import load_dotenv
load_dotenv()
from chromadb import PersistentClient
from rag_engine import process_pdf, query_llm
from auth import *

# Constants
DATA_ROOT = os.getenv("DATA_ROOT", "/mnt/rag-data")
CHROMA_PATH = os.getenv("CHROMA_PATH", os.path.join(DATA_ROOT, "chroma_db"))
USERS_PATH = os.getenv("USERS_PATH", os.path.join(DATA_ROOT, "users"))
USER_DB_FILE = os.getenv("USER_DB_FILE", os.path.join(DATA_ROOT, "users.json"))
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "supersecret")
# Initialize FastAPI
app = FastAPI()

# Verify Admin
def verify_admin(secret: str):
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

# Allow all origins (for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load users
if not os.path.exists(USER_DB_FILE):
    with open(USER_DB_FILE, "w") as f:
        import json
        json.dump({}, f)

# ChromaDB client
chroma_client = PersistentClient(path=CHROMA_PATH)

# ---------------------------- MODELS ---------------------------- #
class AuthRequest(BaseModel):
    username: str
    password: str

class QueryRequest(AuthRequest):
    message: str

# ---------------------------- ROUTES ---------------------------- #
@app.post("/upload_pdf")
async def upload_pdf(
    username: str = Form(...),
    password: str = Form(...),
    file: UploadFile = File(...)
):
    if not authenticate_user(username, password):
        raise HTTPException(status_code=403, detail="Invalid credentials")

    user_dir = os.path.join(USERS_PATH, username, "pdfs")
    os.makedirs(user_dir, exist_ok=True)
    dest_path = os.path.join(user_dir, file.filename)

    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    process_pdf(dest_path, username, chroma_client)
    return {"status": "uploaded and embedded", "file": file.filename}


@app.post("/query")
async def chat_query(request: QueryRequest):
    if not authenticate_user(request.username, request.password):
        raise HTTPException(status_code=403, detail="Invalid credentials")

    answer = query_llm(request.username, request.message, chroma_client)
    return {"response": answer}


@app.post("/list_pdfs")
async def list_user_pdfs(auth: AuthRequest):
    if not authenticate_user(auth.username, auth.password):
        raise HTTPException(status_code=403, detail="Invalid credentials")

    user_dir = os.path.join(USERS_PATH, auth.username, "pdfs")
    if not os.path.exists(user_dir):
        return {"pdfs": []}
    return {"pdfs": os.listdir(user_dir)}


@app.post("/delete_pdf")
async def delete_user_pdf(
    username: str = Form(...),
    password: str = Form(...),
    filename: str = Form(...)
):
    if not authenticate_user(username, password):
        raise HTTPException(status_code=403, detail="Invalid credentials")

    file_path = os.path.join(USERS_PATH, username, "pdfs", filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"status": "deleted", "file": filename}
    else:
        return {"status": "not found", "file": filename}


@app.post("/admin/create_user")
def api_add_user(
    username: str = Form(...),
    password: str = Form(...),
    secret: str = Form(...)
):
    verify_admin(secret)
    if add_user(username, password):
        os.makedirs(os.path.join(USERS_PATH, username, "pdfs"), exist_ok=True)
        os.makedirs(os.path.join(USERS_PATH, username, "chat"), exist_ok=True)
        return {"message": f"✅ User '{username}' created."}
    raise HTTPException(status_code=409, detail="User already exists.")


@app.post("/admin/delete_user")
def api_delete_user(
    username: str = Form(...),
    secret: str = Form(...)
):
    verify_admin(secret)
    if delete_user(username):
        shutil.rmtree(os.path.join(USERS_PATH, username), ignore_errors=True)
        return {"message": f"🗑️ User '{username}' deleted."}
    raise HTTPException(status_code=404, detail="User not found.")

@app.post("/admin/list_users")
def api_list_users(secret: str = Form(...)):
    verify_admin(secret)
    return {"users": list_users()}

@app.get("/")
async def root():
    return {"message": "RAG Backend is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)