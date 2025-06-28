from collections import defaultdict
from bson import ObjectId


class FakeCollection:
    def __init__(self):
        self.storage = {}

    def _normalize_id(self, id_value):
        """Convert ObjectId to string for consistent storage keys"""
        if isinstance(id_value, ObjectId):
            return str(id_value)
        return str(id_value) if id_value else None

    async def find_one(self, filter: dict):
        _id = filter.get("_id")
        if _id is None:
            return None

        # Handle both ObjectId and string inputs
        key = self._normalize_id(_id)
        return self.storage.get(key)

    async def insert_one(self, doc: dict):
        _id = ObjectId()
        doc["_id"] = _id
        # Store using string representation of ObjectId
        self.storage[str(_id)] = doc
        return type("InsertOneResult", (), {"inserted_id": _id})()

    async def update_one(self, filter: dict, update: dict):
        _id = self._normalize_id(filter.get("_id"))
        if _id and _id in self.storage:
            self.storage[_id].update(update["$set"])
            return type("UpdateResult", (), {"modified_count": 1})()
        return type("UpdateResult", (), {"modified_count": 0})()

    async def delete_one(self, filter: dict):
        _id = self._normalize_id(filter.get("_id"))
        if _id and _id in self.storage:
            del self.storage[_id]
            return type("DeleteResult", (), {"deleted_count": 1})()
        return type("DeleteResult", (), {"deleted_count": 0})()


class FakeDB:
    def __init__(self):
        self.collections = defaultdict(FakeCollection)

    def get_collection(self, name: str):
        return self.collections[name]
