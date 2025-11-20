import time
from typing import List
from pymongo import MongoClient, ASCENDING
from .config import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
DB_NAME = os.getenv("DB_NAME", "weatherdb")
COLLECTION = os.getenv("COLLECTION", "snapshots")

class WeatherDAO:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.col = self.client[DB_NAME][COLLECTION]
        self.col.create_index([("city", ASCENDING), ("timestamp_ms", ASCENDING)])

    def save_snapshot(self, snap: dict) -> dict:
        doc = {**snap, 
               "city_key": (snap.get("city") or "").strip().lower(),
               "timestamp_ms": int(time.time() * 1000)}
        self.col.insert_one(doc)
        return doc
    
    def fetch_series(self, city: str, from_ms: int, to_ms: int) -> List[dict]:
        q = { "city_key": (city or "").strip().lower(),
            "timestamp_ms": {"$gte": from_ms, "$lt": to_ms},}
        return list(self.col.find(q).sort("timestamp_ms", ASCENDING))