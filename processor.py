from models import Message
from core.db.crud import add_message_to_mongo
from core.graph.graph import GRAPH
from core.graph.state import ChatState
from langchain_core.messages import HumanMessage, AIMessage
from core.context import get_session_context
from core.session import identify_session


async def _save_bot_message(content: str, session_id: str, phone_number: str):
    bot_msg = Message(
        phone_number=phone_number,
        message_type="text",
        content=content,
        sent_by="bot",
        session_id=session_id,
        status="processed",
    )
    add_message_to_mongo(bot_msg)


async def process_message(message: Message) -> str:
    try:
        session_id = identify_session(message)
        message.session_id = session_id

        session_context = get_session_context(message.phone_number, session_id)
        history = session_context.context_history

        state = ChatState(
            phone_number=message.phone_number,
            session=session_id,
            messages=[
                HumanMessage(content=m.content) if m.sent_by == "user" else AIMessage(content=m.content)
                for m in history
            ] + [HumanMessage(content=message.content)],
        )

        response_state = GRAPH.invoke(state)
        response_data = response_state["messages"][-1]

        message.status = "processed"
        add_message_to_mongo(message)

        if response_data:
            try:
                await _save_bot_message(str(response_data.content), session_id, message.phone_number)
                print(f"\nBot: {response_data.content}")
                return response_data.content
            except Exception as e:
                fallback = f"I encountered an unexpected error. Please try again. ({e})"
                await _save_bot_message(fallback, session_id, message.phone_number)
                print(f"\nBot: {fallback}")
                return fallback
        else:
            fallback = "I couldn't generate a response. Could you try rephrasing that?"
            await _save_bot_message(fallback, session_id, message.phone_number)
            print(f"\nBot: {fallback}")
            return fallback

    except Exception as e:
        fallback = f"I encountered an unexpected error. Please try again. ({e})"
        if message.session_id:
            await _save_bot_message(fallback, message.session_id, message.phone_number)
        print(f"\nBot: {fallback}")
        return fallback
