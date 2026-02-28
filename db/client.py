from pymongo import MongoClient
from dotenv import load_dotenv
import os

env = load_dotenv()

MONGODB_USER = os.getenv("MONGODB_USER")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_CLUSTER = os.getenv("MONGODB_CLUSTER")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

db_client = MongoClient(f"mongodb+srv://{MONGODB_USER}:{MONGODB_PASSWORD}@{MONGODB_CLUSTER}/{MONGODB_DATABASE}").db_timer_nicot

# Query pattern used by timer flow: one active record per task and listing by start.
db_client.records.create_index([("task_id", 1), ("recording", 1)])
db_client.records.create_index("start")
