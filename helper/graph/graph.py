from langgraph.graph import StateGraph, END
from helper.graph.nodes import *
from helper.graph.chat_state import ChatState

GRAPH_BUILDER = StateGraph(ChatState)

# Nodes
GRAPH_BUILDER.add_node("chat", Chat)
GRAPH_BUILDER.add_node("reply_unknown_intents", reply_unknown_intents)
GRAPH_BUILDER.add_node("Identify_Intent" , identify_intent)
GRAPH_BUILDER.add_node("Book_Order" , book_order)

# Graph
GRAPH_BUILDER.set_entry_point("Identify_Intent")
GRAPH_BUILDER.add_conditional_edges(
    "Identify_Intent", 
    path=intent_router, 
    path_map={
    "Chat" : "chat",
    "Unknown": "reply_unknown_intents",
    "Book": "Book_Order"
    }
)
GRAPH_BUILDER.add_edge(["chat", "reply_unknown_intents" , "Book_Order"], END)
GRAPH = GRAPH_BUILDER.compile()