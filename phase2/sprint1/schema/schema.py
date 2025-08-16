# phase2/sprint1/schema/schema.py

from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional, Literal

class CreateLeadSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None

class CreateAccountSchema(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class CreateOrderSchema(BaseModel):
    order_id: str
    customer_id: str
    amount: float
    currency: Literal["USD", "VND", "EUR"]
    status: Literal["pending", "completed", "cancelled"]