from fastapi import APIRouter, HTTPException
from bson.objectid import ObjectId
from database import db
from model import Message

router = APIRouter(prefix="/messages", tags=["Messages"])

def message_serializer(msg) -> dict:
    return {
        "id": str(msg["_id"]),
        "conversation_id": msg["conversation_id"],
        "sender_id": msg["sender_id"],
        "content": msg["content"],
        "created_at": msg["created_at"],
        "updated_at": msg.get("updated_at")
    }

@router.post("/")
async def create_message(msg: Message):
    new_msg = await db["messages"].insert_one(msg.dict(by_alias=True, exclude={"id"}))
    created_msg = await db["messages"].find_one({"_id": new_msg.inserted_id})
    return message_serializer(created_msg)

@router.get("/conversation/{conversation_id}")
async def list_messages(conversation_id: str):
    messages = []
    async for msg in db["messages"].find({"conversation_id": conversation_id}):
        messages.append(message_serializer(msg))
    return messages
