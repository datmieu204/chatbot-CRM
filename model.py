from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timezone

class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")  
    name: str
    email: EmailStr
    password: str
    created_at: datetime = datetime.now(timezone.utc)

    class Config:
        populate_by_name = True  # Cho phép dùng alias khi serialize


class Conversation(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    conversation_name: str
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True

# Request model (FE chỉ cần gửi mấy trường này)
class MessageCreate(BaseModel):
    conversation_id: str
    sender_id: str
    content: str

class Message(MessageCreate):
    id: str = Field(..., alias="id")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # thay cho orm_mode