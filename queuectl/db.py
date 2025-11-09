from pymongo import MongoClient, ASCENDING
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "queuectl")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]


def init_db():
    db.jobs.create_index([("state", ASCENDING)])
    db.jobs.create_index([("next_run_at", ASCENDING)])

    db.config.update_one(
        {"_id": "max_retries"},
        {"$setOnInsert": {"value": 3}},
        upsert=True
    )

    db.config.update_one(
        {"_id": "backoff_base"},
        {"$setOnInsert": {"value": 2}},
        upsert=True
    )

    print(f"Connected to MongoDB at {MONGO_URI}, using database '{DB_NAME}'")
