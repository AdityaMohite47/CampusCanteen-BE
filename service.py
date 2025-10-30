from processor import process_message
from models import Message
from fastapi import FastAPI
from pydantic import BaseModel
import asyncio 
from fastapi.middleware.cors import CORSMiddleware


# Define request body
class ChatRequest(BaseModel):
    message: str

# Define response body
class ChatResponse(BaseModel):
    reply: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # during dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    print("✅ Received message:", request.message)
    reply = await process_message(
        Message(
            student_id="TEST",
            content=request.message,
            sent_by="student"
        ))
    return ChatResponse(reply=reply)