# routes/conversations.py
from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from bson.objectid import ObjectId
from pydantic import BaseModel

from database import db
from model import Conversation

router = APIRouter(prefix="/conversations", tags=["Conversations"])

# --- one-time index ---
_idx_done = False
async def ensure_indexes():
    global _idx_done
    if _idx_done:
        return
    await db["conversations"].create_index([("updated_at", -1)])
    _idx_done = True

# --- serializer ---
def conversation_serializer(conv: dict) -> dict:
    return {
        "id": str(conv["_id"]),
        "conversation_name": conv.get("conversation_name", "New Chat"),
        "created_at": conv.get("created_at"),
        "updated_at": conv.get("updated_at"),
        "latestMessage": conv.get("latestMessage", None),
    }

# GET: danh sách conversations (mới nhất trước)
@router.get("/", response_model=List[dict])
async def get_conversations(limit: int = 50):
    await ensure_indexes()
    cursor = (
        db["conversations"]
        .find({}, {"conversation_name": 1, "created_at": 1, "updated_at": 1, "latestMessage": 1})
        .sort("updated_at", -1)
        .limit(limit)
    )
    convs = await cursor.to_list(length=limit)
    return [conversation_serializer(c) for c in convs]

# POST: tạo conversation mới
@router.post("/", response_model=dict)
async def create_conversation(conv: Conversation):
    await ensure_indexes()

    now = datetime.utcnow()
    doc = conv.model_dump(by_alias=True, exclude={"id"})
    # đảm bảo các trường thời gian được backend set
    doc.setdefault("conversation_name", "New Chat")
    doc["created_at"] = now
    doc["updated_at"] = now
    doc.setdefault("latestMessage", None)

    res = await db["conversations"].insert_one(doc)
    created = await db["conversations"].find_one({"_id": res.inserted_id})
    if not created:
        raise HTTPException(status_code=500, detail="Conversation could not be created")

    return conversation_serializer(created)

# PATCH: đổi tên conversation
class ConversationRenameRequest(BaseModel):
    conversation_name: str


@router.patch("/{conversation_id}/rename", response_model=dict)
async def rename_conversation(conversation_id: str, body: ConversationRenameRequest):
    if not ObjectId.is_valid(conversation_id):
        raise HTTPException(status_code=400, detail="Invalid conversation_id")

    new_name = body.conversation_name.strip()
    if not new_name:
        raise HTTPException(status_code=422, detail="conversation_name must not be empty")

    now = datetime.utcnow()
    result = await db["conversations"].update_one(
        {"_id": ObjectId(conversation_id)},
        {"$set": {"conversation_name": new_name, "updated_at": now}},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")

    updated = await db["conversations"].find_one({"_id": ObjectId(conversation_id)})
    return conversation_serializer(updated)
