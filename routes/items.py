from fastapi import APIRouter, HTTPException
from schemas.item import Item
from database import get_collection
from bson import ObjectId

router = APIRouter()

@router.post("/items/")
async def create_item(item: Item):
    collection = get_collection()
    result = await collection.insert_one(item.dict())
    return {"id": str(result.inserted_id)}

@router.get("/items/{item_id}")
async def read_item(item_id: str):
    collection = get_collection()
    item = await collection.find_one({"_id": ObjectId(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item["id"] = str(item["_id"])
    del item["_id"]
    return item
