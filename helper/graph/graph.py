from langgraph.graph import StateGraph, END
from helper.graph.nodes import *
from helper.graph.chat_state import ChatState

GRAPH_BUILDER = StateGraph(ChatState)

# Nodes
GRAPH_BUILDER.add_node("greet_assistance_response", greet_assistance_response)
GRAPH_BUILDER.add_node("reply_unknown_intents", reply_unknown_intents)
GRAPH_BUILDER.add_node("Identify_Intent" , identify_intent)
GRAPH_BUILDER.add_node("Query_Resolver" , query_resolver)
GRAPH_BUILDER.add_node("Show_Menu" , show_menu)
GRAPH_BUILDER.add_node("Book_Order" , book_order)

# Graph
GRAPH_BUILDER.set_entry_point("Identify_Intent")
GRAPH_BUILDER.add_conditional_edges(
    "Identify_Intent", 
    path=intent_router, 
    path_map={
    "Greet": "greet_assistance_response", 
    "Unknown": "reply_unknown_intents",
    "Query": "Query_Resolver",
    "Menu": "Show_Menu",
    "Book": "Book_Order"
    }
)
GRAPH_BUILDER.add_edge(["greet_assistance_response", "Query_Resolver", "reply_unknown_intents" , "Show_Menu" , "Book_Order"], END)
GRAPH = GRAPH_BUILDER.compile()