import asyncio
import aiohttp
import time
import argparse
import json

# --- Parse command-line arguments ---
parser = argparse.ArgumentParser()
parser.add_argument("--userfile", required=True, help="Path to users.json file")
parser.add_argument("--host", default="http://35.224.171.183:8000", help="API base URL")
parser.add_argument("--queries", type=int, default=4, help="Queries per user")
args = parser.parse_args()

BASE_URL = args.host

# --- Load users from JSON ---
with open(args.userfile, "r") as f:
    users = json.load(f)

QUERY_MESSAGE = "What is this document about?"

# --- Async query function ---
async def send_query(session, username, password, user_id, qid):
    payload = {
        "username": username,
        "password": password,
        "message": QUERY_MESSAGE
    }
    try:
        async with session.post(f"{BASE_URL}/query", json=payload) as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"✅ User {user_id} Q{qid}: {result['response'][:60]}...")
            else:
                print(f"❌ User {user_id} Q{qid}: HTTP {resp.status}")
    except Exception as e:
        print(f"⚠️ User {user_id} Q{qid}: Exception {e}")

# --- Orchestrator ---
async def run_test():
    start = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for user_id, user in enumerate(users):
            username = user["username"]
            password = user["password"]
            for qid in range(args.queries):
                tasks.append(send_query(session, username, password, user_id, qid))
        await asyncio.gather(*tasks)
    end = time.time()
    total_requests = len(users) * args.queries
    print(f"\n⏱️ Completed {total_requests} requests in {end - start:.2f} seconds")

# --- Entry point ---
if __name__ == "__main__":
    asyncio.run(run_test())
