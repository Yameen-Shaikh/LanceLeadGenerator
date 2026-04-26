from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LeadBase(BaseModel):
    name: str
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    score: int = 0
    status: str = "new"
    notes: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class Lead(LeadBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
