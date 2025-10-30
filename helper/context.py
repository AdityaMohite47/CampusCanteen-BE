from models import Message, SessionContext
from helper.mongo.mongodbconn import get_mongodb_connection
from datetime import datetime
from typing import List, Any
import os
import dotenv
dotenv.load_dotenv()

def get_session_context(student_id: str, session_id: str) -> SessionContext:
    conn = get_mongodb_connection()
    sessions_col = conn[os.getenv("SESSIONS_COLLECTION")]
    existing_session = sessions_col.find_one({
        "student_id": student_id,
        "_id": session_id
    })

    if existing_session:
        existing_session["context_history"] = get_session_messages(student_id, session_id)
        existing_session["updated_at"] = datetime.now()
        sessions_col.update_one(
            {"_id": session_id},
            {"$set": {"updated_at": existing_session["updated_at"]}}
        )
        return SessionContext(**existing_session)

    new_session_context = SessionContext(
        student_id=student_id,
        session_id=session_id,
        context_history=[]
    )
    context_data = new_session_context.model_dump(exclude={"context_history"})
    context_data["_id"] = new_session_context.session_id
    context_data["context_history"] = []
    context_data["created_at"] = datetime.now()
    context_data["updated_at"] = datetime.now()
    sessions_col.insert_one(context_data)
    return new_session_context

def update_session_field(session_id: str, field: str, value: Any):
    conn = get_mongodb_connection()
    sessions_col = conn[os.getenv("SESSIONS_COLLECTION")]
    sessions_col.update_one(
        {"_id": session_id},
        {"$set": {field: value, "updated_at": datetime.now()}}
    )

def get_session_messages(student_id: str, session_id: str) -> List[Message]:
    conn = get_mongodb_connection()
    messages_col = conn[os.getenv("MESSAGES_COLLECTION")]
    docs = list(messages_col.find({
        "student_id": student_id,
        "session_id": session_id
    }).sort("created_at", -1))
    return [Message(**msg) for msg in docs]
