from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid, random

class Student(BaseModel):
    student_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Message(BaseModel):
    student_id: str 
    message_type: str = "text" # text / image
    content: str  # Text
    data: Optional[str] = None  # Optional URL to media
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str = "" # Whatsapp message fetched by API provider
    session_id : Optional[str] = None
    sent_by: str  # 'student' or 'bot'
    status: str = "pending" # pending / processed
    created_at: datetime = Field(default_factory=datetime.now)
    
class SessionContext(BaseModel):
    student_id: str 
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    context_history: List[Message] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    status: str = "pending" # pending / completed
    context_language: Optional[str] = None

class Order(BaseModel):
    student_id: Optional[str] = None
    token: int = random.randint(1,999)
    ordered_items: list[dict] = []
    status : Optional[str] = "Pending" # Pending or Served
    payment_status: Optional[str] = "Not Paid" # Paid or Not Paid
    payment_mode: Optional[str] = "Cash" # Cash or UPI
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)