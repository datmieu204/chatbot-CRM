from fastapi import APIRouter, HTTPException
from database import db
from model import Conversation
from typing import List

router = APIRouter(prefix="/conversations", tags=["Conversations"])

# serializer
def conversation_serializer(conv) -> dict:
    return {
        "id": str(conv["_id"]),
        "conversation_name": conv["conversation_name"],
        "created_at": conv["created_at"],
        "updated_at": conv.get("updated_at"),
        # giữ latestMessage nếu backend đã lưu, còn không có thể bỏ
        "latestMessage": conv.get("latestMessage", "")
    }

# Lấy tất cả conversation
@router.get("/", response_model=List[dict])
async def get_conversations():
    convs = await db["conversations"].find().to_list(20)  # lấy tối đa 100 conversation
    return [conversation_serializer(conv) for conv in convs]

# Tạo conversation mới
@router.post("/", response_model=dict)
async def create_conversation(conv: Conversation):
    new_conv = await db["conversations"].insert_one(conv.dict(by_alias=True, exclude={"id"}))
    created_conv = await db["conversations"].find_one({"_id": new_conv.inserted_id})
    if not created_conv:
        raise HTTPException(status_code=500, detail="Conversation could not be created")
    return conversation_serializer(created_conv)
