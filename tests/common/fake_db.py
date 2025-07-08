from collections import defaultdict
from bson import ObjectId
import copy
from typing import Dict, Any, List, Optional


# --- Mock Cursor Class ---
class MockCursor:
    """
    A mock class to simulate AsyncIOMotorCursor behavior for testing.
    It allows chaining of sort, skip, limit, and provides a to_list method.
    """

    def __init__(
        self, data: List[Dict[str, Any]], projection: Optional[Dict[str, Any]] = None
    ):
        self._data = data
        self._projection = projection
        self._sort_criteria = None
        self._skip_value = None
        self._limit_value = None

    def sort(self, sort_criteria: Dict[str, Any]):
        """Simulates the .sort() method of a Motor cursor."""
        self._sort_criteria = sort_criteria
        return self

    def skip(self, skip_value: int):
        """Simulates the .skip() method of a Motor cursor."""
        self._skip_value = skip_value
        return self

    def limit(self, limit_value: int):
        """Simulates the .limit() method of a Motor cursor."""
        self._limit_value = limit_value
        return self

    async def to_list(self, length: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Simulates the .to_list() method of a Motor cursor.
        Applies sorting, skipping, and limiting to the internal data.
        """
        results = copy.deepcopy(self._data)  # Work on a copy

        if self._sort_criteria:
            for sort_field, sort_order in reversed(list(self._sort_criteria.items())):
                # Ensure the field exists for stable sorting, or handle missing fields
                results.sort(
                    key=lambda x: x.get(sort_field, None), reverse=(sort_order == -1)
                )

        # Apply skip
        if self._skip_value is not None and self._skip_value > 0:
            results = results[self._skip_value :]

        # Apply limit
        if self._limit_value is not None and self._limit_value >= 0:
            results = results[: self._limit_value]

        # Apply projection to the final results
        final_results = [
            self._apply_projection(doc, self._projection) for doc in results
        ]

        return final_results

    def _apply_projection(self, doc: dict, projection: Optional[dict]) -> dict:
        """Helper to apply projection to a single document."""
        if projection is None:
            return doc

        projected_doc = {}
        # Handle inclusion projection (e.g., {"field": 1})
        if any(v == 1 for v in projection.values()):
            # _id is included by default unless explicitly excluded
            if "_id" not in projection or projection["_id"] == 1:
                if "_id" in doc:
                    projected_doc["_id"] = doc["_id"]
            for key, value in projection.items():
                if value == 1 and key in doc:
                    projected_doc[key] = doc[key]
        # Handle exclusion projection (e.g., {"field": 0})
        elif any(v == 0 for v in projection.values()):
            projected_doc = copy.deepcopy(doc)
            for key, value in projection.items():
                if value == 0 and key in projected_doc:
                    del projected_doc[key]
            # _id is included by default unless explicitly excluded
            if "_id" in doc and projection.get("_id") == 0:
                if "_id" in projected_doc:
                    del projected_doc["_id"]
            elif "_id" in doc and "_id" not in projected_doc:
                projected_doc["_id"] = doc["_id"]
        else:
            return (
                doc  # If projection is mixed or invalid, return full doc for simplicity
            )

        return projected_doc

    async def count_documents(self) -> int:
        """Simulates count_documents for find_one's internal logic."""
        return len(self._data)


# --- FakeCollection Class ---
class FakeCollection:
    def __init__(self):
        self.storage = {}

    def _normalize_id(self, id_value: Any) -> Optional[str]:
        """Convert ObjectId to string for consistent storage keys."""
        if isinstance(id_value, ObjectId):
            return str(id_value)
        return str(id_value) if id_value else None

    def _matches_filter(self, doc: dict, filter: dict) -> bool:
        """Simple filter matching for demonstration. Extend for full MongoDB query language."""
        if not filter:
            return True
        for key, value in filter.items():
            if key == "_id":
                # Special handling for _id to match both ObjectId and string forms
                if self._normalize_id(doc.get("_id")) != self._normalize_id(value):
                    return False
            elif doc.get(key) != value:  # Simple equality check
                return False
        return True

    async def find_one(
        self,
        query: dict,
        # Removed projection and sort parameters to match the new signature
    ) -> Optional[dict]:
        """
        Finds a single document matching the query.
        Projection and sort are no longer handled at this level for find_one.
        """
        for doc_id, doc in self.storage.items():
            if self._matches_filter(doc, query):
                return copy.deepcopy(doc)
        return None

    def find(
        self,
        query: dict,
        projection: Optional[dict] = None,
    ) -> MockCursor:
        """
        Simulates the collection.find() method, returning a MockCursor directly.
        The filtering by query is done here before creating the cursor.
        """
        filtered_results = []
        for doc_id, doc in self.storage.items():
            if self._matches_filter(doc, query):
                filtered_results.append(copy.deepcopy(doc))

        return MockCursor(filtered_results, projection)

    async def insert_one(self, doc: dict):
        """Inserts a single document."""
        _id = doc.get("_id", ObjectId())
        if not isinstance(_id, ObjectId):
            try:
                _id = ObjectId(str(_id))
            except:
                _id = ObjectId()

        doc_to_store = copy.deepcopy(doc)
        doc_to_store["_id"] = _id
        self.storage[str(_id)] = doc_to_store

        class MockInsertOneResult:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id

        return MockInsertOneResult(_id)

    async def insert_many(self, docs: List[dict]):
        """Inserts multiple documents."""
        inserted_ids = []
        for doc in docs:
            _id = doc.get("_id", ObjectId())
            if not isinstance(_id, ObjectId):
                try:
                    _id = ObjectId(str(_id))
                except:
                    _id = ObjectId()

            doc_to_store = copy.deepcopy(doc)
            doc_to_store["_id"] = _id
            self.storage[str(_id)] = doc_to_store
            inserted_ids.append(_id)

        class MockInsertManyResult:
            def __init__(self, inserted_ids):
                self.inserted_ids = inserted_ids

        return MockInsertManyResult(inserted_ids)

    async def update_one(self, filter: dict, update: dict):
        """Updates a single document."""
        modified_count = 0
        for doc_id, doc in self.storage.items():
            if self._matches_filter(doc, filter):
                if "$set" in update:
                    doc.update(update["$set"])
                    modified_count = 1
                    break

        class MockUpdateResult:
            def __init__(self, modified_count):
                self.modified_count = modified_count

        return MockUpdateResult(modified_count)

    async def update_many(self, filter: dict, update: dict):
        """Updates multiple documents."""
        modified_count = 0
        for doc_id, doc in self.storage.items():
            if self._matches_filter(doc, filter):
                if "$set" in update:
                    doc.update(update["$set"])
                    modified_count += 1

        class MockUpdateResult:
            def __init__(self, modified_count):
                self.modified_count = modified_count

        return MockUpdateResult(modified_count)

    async def delete_one(self, filter: dict):
        """Deletes a single document."""
        deleted_count = 0
        keys_to_delete = []
        for doc_id, doc in self.storage.items():
            if self._matches_filter(doc, filter):
                keys_to_delete.append(doc_id)
                break

        for key in keys_to_delete:
            del self.storage[key]
            deleted_count = 1  # Only one can be deleted by delete_one

        class MockDeleteResult:
            def __init__(self, deleted_count):
                self.deleted_count = deleted_count

        return MockDeleteResult(deleted_count)

    async def delete_many(self, filter: dict):
        """Deletes multiple documents."""
        deleted_count = 0
        keys_to_delete = []
        for doc_id, doc in self.storage.items():
            if self._matches_filter(doc, filter):
                keys_to_delete.append(doc_id)

        for key in keys_to_delete:
            del self.storage[key]
            deleted_count += 1

        class MockDeleteResult:
            def __init__(self, deleted_count):
                self.deleted_count = deleted_count

        return MockDeleteResult(deleted_count)


# --- FakeDB Class ---
class FakeDB:
    def __init__(self):
        self.collections = defaultdict(FakeCollection)

    def get_collection(self, name: str) -> FakeCollection:
        """Returns a FakeCollection instance for the given name."""
        return self.collections[name]
