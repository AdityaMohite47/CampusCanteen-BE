from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from typing import Annotated , List
from langchain_core.messages import AIMessage , HumanMessage

class ChatState(TypedDict):
    phone_number : str
    session: str
    messages: Annotated[List[AIMessage | HumanMessage] , add_messages]
    active_intent : str