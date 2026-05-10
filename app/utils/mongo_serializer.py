from bson import ObjectId
from typing import Any, Dict, List, Union, TypeVar, Optional
from beanie import Document
from pydantic import BaseModel

T = TypeVar("T")

class MongoSerializer:
    """
    Professional MongoDB document serializer for FastAPI & Pydantic v2.
    Handles ObjectId conversion, _id to id mapping, and recursive serialization.
    """

    @staticmethod
    def to_dict(obj: Any) -> Any:
        """
        Recursively converts MongoDB documents, Beanie models, and Pydantic models 
        into JSON-serializable dictionaries.
        """
        if obj is None:
            return None

        # 1. Handle Beanie Documents or Pydantic Models
        if isinstance(obj, (Document, BaseModel)):
            # We use model_dump() to get the raw dictionary representation
            obj = obj.model_dump()

        # 2. Handle Lists/Iterables
        if isinstance(obj, list):
            return [MongoSerializer.to_dict(item) for item in obj]

        # 3. Handle Dictionaries
        if isinstance(obj, dict):
            new_dict = {}
            for key, value in obj.items():
                # Convert _id to id for frontend compatibility
                new_key = "id" if key == "_id" else key
                new_dict[new_key] = MongoSerializer.to_dict(value)
            return new_dict

        # 4. Handle ObjectId conversion to String
        if isinstance(obj, ObjectId):
            return str(obj)

        # 5. Handle everything else (int, str, float, datetime, etc.)
        return obj

def serialize_doc(data: T) -> Dict[str, Any]:
    """Helper to serialize a single document/object."""
    return MongoSerializer.to_dict(data)

def serialize_list(data: List[T]) -> List[Dict[str, Any]]:
    """Helper to serialize a list of documents/objects."""
    if not data:
        return []
    return [MongoSerializer.to_dict(item) for item in data]
