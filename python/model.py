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


class Message(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    conversation_id: str
    sender_id: str  
    content: str
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
