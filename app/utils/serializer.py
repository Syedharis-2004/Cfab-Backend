from bson import ObjectId
from typing import Any, Dict, List, Union
from beanie import Document
from pydantic import BaseModel

def convert_ids(obj: Any) -> Any:
    """
    Recursively converts MongoDB ObjectId fields to strings and replaces '_id' with 'id'.
    Handles lists, dictionaries, Beanie documents, and Pydantic models.
    """
    if obj is None:
        return None

    # Handle Beanie documents or Pydantic models
    if isinstance(obj, (Document, BaseModel)):
        obj = obj.model_dump()

    if isinstance(obj, list):
        return [convert_ids(item) for item in obj]

    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            # Replace _id with id
            new_key = "id" if key == "_id" else key
            new_dict[new_key] = convert_ids(value)
        return new_dict

    if isinstance(obj, ObjectId):
        return str(obj)

    return obj

def serialize_list(items: List[Any]) -> List[Dict[str, Any]]:
    """Helper to serialize a list of items."""
    return [convert_ids(item) for item in items]

def serialize_dict(item: Any) -> Dict[str, Any]:
    """Helper to serialize a single item."""
    return convert_ids(item)
