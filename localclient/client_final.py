import requests
import json
import os

# --- CONFIG ---
BASE_URL = "http://35.224.171.183:8000"  # Replace with your FastAPI public IP
ADMIN_SECRET = "supersecret"
USERS_JSON = "users.json"

# --- LOCAL USER RECORDS ---
def load_users():
    if not os.path.exists(USERS_JSON):
        return []
    with open(USERS_JSON, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_JSON, "w") as f:
        json.dump(users, f, indent=4)

def add_user_local(username, password):
    users = load_users()
    if not any(u["username"] == username for u in users):
        users.append({"username": username, "password": password})
        save_users(users)

def delete_user_local(username):
    users = load_users()
    updated_users = [u for u in users if u["username"] != username]
    if len(updated_users) != len(users):
        save_users(updated_users)

# --- BACKEND FUNCTIONS ---
def create_user(username, password):
    url = f"{BASE_URL}/admin/create_user"
    data = {"username": username, "password": password, "secret": ADMIN_SECRET}
    response = requests.post(url, data=data)
    print("✅ Create User:", response.status_code, response.text)
    if response.status_code == 200:
        add_user_local(username, password)
    elif "already exists" in response.text:
        print("ℹ️ User already exists.")

def delete_user(username):
    url = f"{BASE_URL}/admin/delete_user"
    data = {"username": username, "secret": ADMIN_SECRET}
    response = requests.post(url, data=data)
    print("🗑️ Delete User:", response.status_code, response.text)
    if response.status_code == 200:
        delete_user_local(username)

def list_users():
    url = f"{BASE_URL}/admin/list_users"
    data = {"secret": ADMIN_SECRET}
    response = requests.post(url, data=data)
    print("📋 List Users:", response.status_code)
    try:
        print(response.json())
    except:
        print("❌ Failed to parse response.")

def upload_pdf(username, password, filepath):
    url = f"{BASE_URL}/upload_pdf"
    with open(filepath, "rb") as f:
        files = {"file": (os.path.basename(filepath), f)}
        data = {"username": username, "password": password}
        response = requests.post(url, files=files, data=data)
    print("📄 Upload PDF:", response.status_code, response.text)

def list_pdfs(username, password):
    url = f"{BASE_URL}/list_pdfs"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data)
    print("📚 List PDFs:", response.status_code)
    try:
        print(response.json())
    except:
        print("❌ Failed to parse response.")

def delete_pdf(username, password, filename):
    url = f"{BASE_URL}/delete_pdf"
    data = {"username": username, "password": password, "filename": filename}
    response = requests.post(url, data=data)
    print("🗑️ Delete PDF:", response.status_code, response.text)

def query_pdf(username, password, message):
    url = f"{BASE_URL}/query"
    data = {"username": username, "password": password, "message": message}
    response = requests.post(url, json=data)
    print("💬 Query:", response.status_code)
    try:
        print(response.json())
    except:
        print("❌ Failed to parse response.")

# --- MAIN LOOP ---
if __name__ == "__main__":
    print("🚀 AI RAG Client Interface")

    while True:
        print("\nAvailable operations:")
        print("  create_user   - Create a user")
        print("  delete_user   - Delete a user")
        print("  upload_pdf    - Upload a PDF for a user")
        print("  list_pdfs     - List PDFs for a user")
        print("  delete_pdf    - Delete a PDF")
        print("  query_pdf     - Ask a question")
        print("  list_users    - List all users")
        print("  quit          - Exit the client")

        action = input("👉 Choose operation: ").strip().lower()

        if action == "quit":
            print("👋 Exiting client.")
            break

        if action == "list_users":
            list_users()
        elif action in ["create_user", "delete_user", "upload_pdf", "list_pdfs", "delete_pdf", "query_pdf"]:
            username = input("👤 Enter username: ").strip()
            password = input("🔐 Enter password: ").strip()

            if action == "create_user":
                create_user(username, password)
            elif action == "delete_user":
                delete_user(username)
            elif action == "upload_pdf":
                filepath = input("📁 Enter full PDF file path: ").strip()
                if not os.path.exists(filepath):
                    print("❌ File does not exist.")
                else:
                    upload_pdf(username, password, filepath)
            elif action == "list_pdfs":
                list_pdfs(username, password)
            elif action == "delete_pdf":
                filename = input("🗑️ Enter filename to delete: ").strip()
                delete_pdf(username, password, filename)
            elif action == "query_pdf":
                question = input("💬 Enter your question: ").strip()
                query_pdf(username, password, question)
        else:
            print("❌ Invalid operation selected.")
