from fastapi import APIRouter
from database import db
from model import Conversation
from typing import List

router = APIRouter(prefix="/conversations", tags=["Conversations"])

def conversation_serializer(conv) -> dict:
    return {
        "id": str(conv["_id"]),
        "conversation_name": conv["conversation_name"],
        "created_at": conv["created_at"],
        "updated_at": conv.get("updated_at"),
        "latestMessage": conv.get("latestMessage", "")  # nếu backend đã lưu latestMessage
    }

@router.get("/", response_model=List[dict])
async def get_conversations():
    convs = await db["conversations"].find().to_list(10)
    return [conversation_serializer(conv) for conv in convs]
