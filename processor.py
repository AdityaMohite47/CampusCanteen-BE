from models import Message
from helper.mongo.mongo_helper import update_message , add_message_to_mongo
from helper.graph.graph import GRAPH
from helper.graph.chat_state import ChatState
from langchain_core.messages import HumanMessage , AIMessage
from helper.context import get_session_context
from helper.session import identify_session

async def add_bot_message_to_mongo(msg : str , session_id : str , student_id : str):
    BotMessage = Message(
            student_id=student_id,
            message_type="text",
            content=msg,
            sent_by="bot",
            session_id=session_id,
            status="processed"
        )
    add_message_to_mongo(BotMessage)
    return

async def process_message(message: Message) -> str:
    try:
        session_id = identify_session(message)
        message.session_id = session_id
        update_message(message)
        
        session_context = get_session_context(message.student_id , session_id)
        session_history = session_context.context_history
        state = ChatState(
            student_id = message.student_id,
            session = session_id,
            messages = [HumanMessage(content=msg.content) if msg.sent_by == "student" else AIMessage(content=msg.content) for msg in session_history] + [HumanMessage(content=message.content)],
        )
        
        response_state = GRAPH.invoke(state)
        response_data = response_state["messages"][-1]
    
        
        if response_data is not None and str(response_data).strip():
            message.status = "processed"
            update_message(message)
            add_message_to_mongo(message)   
            try:
                await add_bot_message_to_mongo(str(response_data.content), message.session_id, message.student_id)
                print(f"\nBot: {response_data.content}")
                return response_data.content
            except Exception as e:
                fallback_message = f"I encountered an unexpected error, Can you please try again? {e}"  
                message.content = fallback_message
                await add_bot_message_to_mongo(fallback_message, message.session_id, message.student_id)
                print("\nBot: " + fallback_message) 
                return fallback_message
        else:
            fallback_message = "I'm sorry, I couldn't generate a response. Could you try rephrasing that?"  
            message.content = fallback_message
            await add_bot_message_to_mongo(fallback_message, message.session_id, message.student_id)
            print(f"\nBot: {fallback_message}")
            return fallback_message
    except Exception as e:
        fallback_message = f"I encountered an unexpected error, Can you please try again? {e}"  
        message.content = fallback_message
        add_message_to_mongo(message)
        await add_bot_message_to_mongo(fallback_message, message.session_id, message.student_id)
        print("\nBot: " + fallback_message)   
        return fallback_message