from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from processor import process_message
from models import Message

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"]
)

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    user_message = req.message
    reply = await process_message(
        Message(
            phone_number="TEST",
            content=user_message,
            sent_by="user"
        ))
    return {"response": reply}