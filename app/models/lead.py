from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.database.database import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String, nullable=True)
    website = Column(String, nullable=True)
    address = Column(String, nullable=True)
    score = Column(Integer, default=0)
    status = Column(String, default="new") # new, contacted, closed
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
