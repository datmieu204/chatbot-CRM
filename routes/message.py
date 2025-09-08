from fastapi import APIRouter, HTTPException
from bson.objectid import ObjectId
from database import db
from datetime import datetime
from model import Message, MessageCreate
from typing import List

router = APIRouter(prefix="/messages", tags=["Messages"])


def message_serializer(msg) -> dict:
    return {
        "id": str(msg["_id"]),
        "conversation_id": msg["conversation_id"],
        "sender_id": msg["sender_id"],
        "content": msg["content"],
        "created_at": msg["created_at"],
        "updated_at": msg.get("updated_at"),
    }


@router.post("/", response_model=Message)
async def create_message(msg: MessageCreate):
    try:
        data = msg.dict()
        data["created_at"] = datetime.utcnow().isoformat()
        data["updated_at"] = datetime.utcnow().isoformat()

        new_msg = await db["messages"].insert_one(data)
        created_msg = await db["messages"].find_one({"_id": new_msg.inserted_id})

        if not created_msg:
            raise HTTPException(status_code=500, detail="Message creation failed")

        return message_serializer(created_msg)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating message: {str(e)}")


@router.get("/conversation/{conversation_id}", response_model=List[Message])
async def list_messages(conversation_id: str):
    try:
        if not ObjectId.is_valid(conversation_id):
            raise HTTPException(status_code=400, detail="Invalid conversation_id")

        messages = []
        async for msg in db["messages"].find({"conversation_id": conversation_id}):
            messages.append(message_serializer(msg))

        return messages

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching messages: {str(e)}")
