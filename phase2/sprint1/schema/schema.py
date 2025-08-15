# phase2/sprint1/schema/schema.py

from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional, Literal

class CreateLeadSchema(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    company: Optional[str]
    notes: Optional[str]

class CreateAccountSchema(BaseModel):
    company_name: Optional[str]
    industry: Optional[str]
    website: Optional[HttpUrl]

class CreateOrderSchema(BaseModel):
    order_id: str
    customer_id: str
    amount: float
    currency: Literal["USD", "VND", "EUR"]
    status: Literal["pending", "completed", "cancelled"]