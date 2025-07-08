from typing import Any, Dict, List, Optional
from app.utils.db_utils.db_utils import BaseCollectionOperations
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult


class MongoCollectionOperations(BaseCollectionOperations[AsyncIOMotorDatabase]):
    """
    Concrete implementation of BaseCollectionOperations for MongoDB (using Motor).
    """

    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str):
        """
        Initializes MongoCollectionOperations for a specific MongoDB database and collection.

        Args:
            db (AsyncIOMotorDatabase): The Motor MongoDB database instance.
            collection_name (str): The name of the collection to operate on.
        """
        super().__init__(db, collection_name)
        self._collection = self._db_connection.get_collection(
            self._collection_or_table_name
        )

    async def find_one(
        self,
        query: Dict[str, Any],
        # projection: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Finds a single document in the MongoDB collection with optional projection and sort."""
        return await self._collection.find_one(query)

    async def find_many(
        self,
        query: Dict[str, Any] = None,
        projection: Optional[Dict[str, Any]] = None,
        sort: Optional[Dict[str, Any]] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Finds multiple documents in the MongoDB collection and returns them as a list,
        with optional projection, sort, skip, and limit.
        """
        if query is None:
            query = {}

        cursor = self._collection.find(query, projection)

        if sort:
            cursor = cursor.sort(sort)
        if skip is not None:
            cursor = cursor.skip(skip)
        if limit is not None:
            cursor = cursor.limit(limit)

        return await cursor.to_list(length=None)

    async def insert_one(self, document: Dict[str, Any]) -> InsertOneResult:
        """Inserts a single document into the MongoDB collection."""
        return await self._collection.insert_one(document)

    async def insert_many(self, documents: List[Dict[str, Any]]) -> InsertOneResult:
        """Inserts multiple documents into the MongoDB collection."""
        return await self._collection.insert_many(documents)

    async def update_one(
        self, query: Dict[str, Any], update_data: Dict[str, Any]
    ) -> UpdateResult:
        """
        Updates a single document in the MongoDB collection.
        Note: update_data here should be the full MongoDB update document (e.g., {"$set": {"field": "value"}}).
        """
        return await self._collection.update_one(query, update_data)

    async def update_many(
        self, query: Dict[str, Any], update_data: Dict[str, Any]
    ) -> UpdateResult:
        """
        Updates multiple documents in the MongoDB collection.
        Note: update_data here should be the full MongoDB update document (e.g., {"$set": {"field": "value"}}).
        """
        return await self._collection.update_many(query, update_data)

    async def delete_one(self, query: Dict[str, Any]) -> DeleteResult:
        """Deletes a single document from the MongoDB collection."""
        return await self._collection.delete_one(query)

    async def delete_many(self, query: Dict[str, Any] = None) -> DeleteResult:
        """Deletes multiple documents from the MongoDB collection."""
        if query is None:
            query = {}
        return await self._collection.delete_many(query)
