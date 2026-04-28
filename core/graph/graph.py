from langgraph.graph import StateGraph, END
from core.graph.nodes import (
    reply_unknown_intents,
    identify_intent, intent_router,
    chat_menu, chat_general,
    book_order,
)
from core.graph.state import ChatState

GRAPH_BUILDER = StateGraph(ChatState)

GRAPH_BUILDER.add_node("identify_intent", identify_intent)
GRAPH_BUILDER.add_node("chat_menu", chat_menu)
GRAPH_BUILDER.add_node("chat_general", chat_general)
GRAPH_BUILDER.add_node("book_order", book_order)
GRAPH_BUILDER.add_node("reply_unknown_intents", reply_unknown_intents)

GRAPH_BUILDER.set_entry_point("identify_intent")

GRAPH_BUILDER.add_conditional_edges(
    "identify_intent",
    path=intent_router,
    path_map={
        "MenuQuery": "chat_menu",
        "General":   "chat_general",
        "Book":      "book_order",
        "Unknown":   "reply_unknown_intents",
    }
)

GRAPH_BUILDER.add_edge(["chat_menu", "chat_general", "book_order", "reply_unknown_intents"], END)

GRAPH = GRAPH_BUILDER.compile()
