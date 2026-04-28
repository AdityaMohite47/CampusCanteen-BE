from typing import Annotated, List
from typing_extensions import TypedDict
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph.message import add_messages


class ChatState(TypedDict):
    phone_number: str
    session: str
    messages: Annotated[List[AIMessage | HumanMessage], add_messages]
    active_intent: str  # "MenuQuery" | "General" | "Book" | "Unknown"
