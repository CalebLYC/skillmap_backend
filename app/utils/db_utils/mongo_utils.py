from typing import Any, Dict, List, Optional
from app.utils.db_utils.db_utils import BaseCollectionOperations
from motor.motor_asyncio import AsyncIOMotorDatabase


class MongoCollectionOperations(BaseCollectionOperations[AsyncIOMotorDatabase]):
    """
    Concrete implementation of BaseCollectionOperations for MongoDB (using Motor).
    This class maps Motor's specific return types to the generic types defined
    in BaseCollectionOperations.
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
    ) -> Optional[Dict[str, Any]]:
        """Finds a single document in the MongoDB collection."""
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

    async def insert_one(self, document: Dict[str, Any]) -> str:
        """Inserts a single document into the MongoDB collection, returning its ID as a string."""
        result = await self._collection.insert_one(document)
        return str(result.inserted_id)

    async def insert_many(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Inserts multiple documents into the MongoDB collection, returning their IDs as strings."""
        result = await self._collection.insert_many(documents)
        return [str(id) for id in result.inserted_ids]

    async def update_one(
        self, query: Dict[str, Any], update_data: Dict[str, Any]
    ) -> int:
        """
        Updates a single document in the MongoDB collection, returning the number of modified documents.
        Note: update_data here should be the full MongoDB update document (e.g., {"$set": {"field": "value"}}).
        """
        result = await self._collection.update_one(query, update_data)
        return result.modified_count

    async def update_many(
        self, query: Dict[str, Any], update_data: Dict[str, Any]
    ) -> int:
        """
        Updates multiple documents in the MongoDB collection, returning the number of modified documents.
        Note: update_data here should be the full MongoDB update document (e.g., {"$set": {"field": "value"}}).
        """
        result = await self._collection.update_many(query, update_data)
        return result.modified_count

    async def delete_one(self, query: Dict[str, Any]) -> int:
        """Deletes a single document from the MongoDB collection, returning the number of deleted documents."""
        result = await self._collection.delete_one(query)
        return result.deleted_count

    async def delete_many(self, query: Dict[str, Any] = None) -> int:
        """Deletes multiple documents from the MongoDB collection, returning the number of deleted documents."""
        if query is None:
            query = {}
        result = await self._collection.delete_many(query)
        return result.deleted_count
