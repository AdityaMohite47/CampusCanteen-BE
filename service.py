from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from processor import process_message
from models import Message

app = FastAPI(title="CampusCanteen API")


class MessageRequest(BaseModel):
    phone_number: str
    content: str
    message_type: str = "text"
    source: str = ""

class MessageResponse(BaseModel):
    reply: str
    phone_number: str

@app.post("/message", response_model=MessageResponse)
async def receive_message(req: MessageRequest):
    msg = Message(
        phone_number=req.phone_number,
        content=req.content,
        message_type=req.message_type,
        source=req.source,
        sent_by="user",
    )
    try:
        reply = await process_message(msg)
        return MessageResponse(reply=reply, phone_number=req.phone_number)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
