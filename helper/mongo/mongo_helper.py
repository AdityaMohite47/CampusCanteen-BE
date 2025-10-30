from typing import Optional, List, Any,TypedDict
from datetime import datetime
from pymongo.errors import PyMongoError
from models import *
from .mongodbconn import get_mongodb_connection
import dotenv, os
dotenv.load_dotenv()

def add_message_to_mongo(message: Message):
    conn = get_mongodb_connection()
    message_collection = conn[os.getenv("MESSAGES_COLLECTION")]
    students_collection = conn[os.getenv("STUDENTS_COLLECTION")]

    student = students_collection.find_one({"student_id": message.student_id})
    if not student:
        add_user_to_mongo(Student(student_id=message.student_id))

    doc = message.model_dump()
    try:
        result = message_collection.insert_one(doc)
        append_message_to_session(message.student_id, message.session_id, message)
        return result.inserted_id
    except PyMongoError as e:
        raise e
    

def append_message_to_session(student_id: str, session_id: str, message: Message):
    conn = get_mongodb_connection()
    session_collection = conn[os.getenv("SESSIONS_COLLECTION")]
    
    try:
        session = session_collection.find_one({"student_id": student_id, "session_id": session_id})
        if session:
            session["context_history"].append(message.model_dump())
            session_collection.update_one({"student_id": student_id, "session_id": session_id}, {"$set": {"context_history": session["context_history"]}})
        else:
            raise ValueError("Session not found")
    except PyMongoError as e:
        raise e
    
def add_user_to_mongo(student: Student):
    conn = get_mongodb_connection()
    student_collection = conn[os.getenv("STUDENTS_COLLECTION")]   
    try:
        result = student_collection.insert_one(student.model_dump())
        return result.inserted_id
    except PyMongoError as e:
        raise e

def add_session_to_mongo(session: SessionContext):
    conn = get_mongodb_connection()
    session_collection = conn[os.getenv("SESSIONS_COLLECTION")]
    
    try:
        result = session_collection.insert_one(session.model_dump())
        return result.inserted_id
    except PyMongoError as e:
        raise e
    
def add_order_to_mongo(order: Order):
    conn = get_mongodb_connection()
    order_collection = conn[os.getenv("ORDERS_COLLECTION")]

    try:
        result = order_collection.insert_one(order.model_dump())
        return result.inserted_id
    except PyMongoError as e:
        raise e
    
def fetch_menu():
    conn = get_mongodb_connection()
    menu_collection = conn[os.getenv("MENU_COLLECTION")]
    try:
        food_items = list(menu_collection.find({}))
        for item in food_items:
            item['_id'] = str(item['_id']) 
        return food_items
    except PyMongoError as e:
        raise PyMongoError(f"Failed to fetch vendors: {str(e)}")
    
def fetch_last_n_messages(student_id: str, n: int = 10) -> List[Message]:
    conn = get_mongodb_connection()
    message_collection = conn[os.getenv("MESSAGES_COLLECTION")]
    
    try:
        messages = message_collection.find({"student_id": student_id}).sort("created_at", -1).limit(n)
        return [Message(**msg) for msg in messages]
    except PyMongoError as e:
        raise e

def get_last_message(student_id: str) -> Optional[Message]:
    conn = get_mongodb_connection()
    message_collection = conn[os.getenv("MESSAGES_COLLECTION")]
    
    try:
        message = message_collection.find_one({"student_id": student_id}, sort=[("created_at", -1)])
        return Message(**message) if message else None
    except PyMongoError as e:
        raise e
    
def update_message(message : Message):
    conn = get_mongodb_connection()
    message_collection = conn[os.getenv("MESSAGES_COLLECTION")]
    
    student = conn[os.getenv("STUDENTS_COLLECTION")].find_one({"student_id" : message.student_id})
    if not student:
        add_user_to_mongo(Student(student_id=message.student_id))
    try:
        message_collection.update_one({"_id": message.message_id}, {"$set": message.model_dump()})
    except PyMongoError as e:
        raise e