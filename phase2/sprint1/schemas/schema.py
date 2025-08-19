# phase2/sprint1/schema/schema.py

from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional, Literal



class CreateLeadSchema(BaseModel):
    name: str = Field(..., description="Full name of the lead")
    email: EmailStr = Field(..., description="Email address of the lead")
    phone: str = Field(..., description="Phone number of the lead")
    company: Optional[str] = Field(
        None, description="Company name (optional)", json_schema_extra={"nullable": True}
    )
    notes: Optional[str] = Field(
        None, description="Additional notes (optional)", json_schema_extra={"nullable": True}
    )

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