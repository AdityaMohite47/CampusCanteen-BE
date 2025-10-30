from processor import process_message
from models import Message
import asyncio

# Build initial ChatState dict
STUDENT_ID = input("Enter your student ID : ").strip()

async def chat_loop():
    print("\nType your message below. Type 'exit' to quit.\n")
    while True:
        user_input = input("\nYou: ").strip() 
        if user_input.lower() in {"exit", "quit"}:
            print("Exiting chat.")
            break
        msg = Message(
            student_id=STUDENT_ID,
            content=user_input,
            sent_by="student"
        )
        try:
            await process_message(msg)
        except Exception as e:
            print("Error processing message:", e)

if __name__ == "__main__":
    asyncio.run(chat_loop())