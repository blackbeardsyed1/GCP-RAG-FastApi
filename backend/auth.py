import os
import json
import bcrypt

# Constants
USER_DB_PATH = "/mnt/rag-data/users.json"

# Ensure the file exists
if not os.path.exists(USER_DB_PATH):
    with open(USER_DB_PATH, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USER_DB_PATH, "r") as f:
        return json.load(f)

def list_users():
    users = load_users()
    return list(users.keys())

def save_users(users):
    with open(USER_DB_PATH, "w") as f:
        json.dump(users, f, indent=4)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def add_user(username: str, password: str) -> bool:
    users = load_users()
    if username in users:
        return False  # User already exists
    users[username] = hash_password(password)
    save_users(users)
    return True

def delete_user(username: str) -> bool:
    users = load_users()
    if username not in users:
        return False
    users.pop(username)
    save_users(users)
    return True

def authenticate_user(username: str, password: str) -> bool:
    users = load_users()
    if username not in users:
        return False
    return verify_password(password, users[username])