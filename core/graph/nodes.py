import random, json
from core.graph.state import ChatState
from langchain_core.messages import AIMessage
from core.llm import LLM
from core.graph.prompts import CHAT_PROMPT, GENERAL_CHAT_PROMPT, INTENT_PROMPT, BOOK_ORDER_PROMPT
from core.db.crud import add_order_to_mongo, fetch_menu
from core.graph.utils import sanitize_llm_json
from models import Order


def reply_unknown_intents(state: ChatState):
    fallback_responses = [
        "I'm here to help with canteen-related questions. You can ask about today's menu, booking food, or payment options.",
        "I specialize in food ordering help. If you're looking for the menu or want to prebook a meal, I've got you covered.",
        "That's a bit outside my zone. Try asking about menu items, booking your meal, or payment methods.",
        "I'm focused on helping you order from the canteen. Want to check the menu or place a prebook order?",
        "My focus is on food ordering, payments, and helping you with your canteen orders.",
    ]
    return {"messages": [AIMessage(content=random.choice(fallback_responses))]}


def identify_intent(state: ChatState):
    recent_msgs = [msg.content for msg in state["messages"][-3:]]

    try:
        intent = LLM.invoke([
            INTENT_PROMPT,
            json.dumps({
                "conversation_history": recent_msgs[:-1],
                "current_message": recent_msgs[-1],
            })
        ])
        result = intent.content.strip()
        if result not in ("MenuQuery", "General", "Book", "Unknown"):
            result = "General"
    except Exception as e:
        print(f"ERROR IDENTIFYING INTENT: {e}")
        result = "General"

    print(f"Intent: {result}")
    return {"active_intent": result}


def intent_router(state: ChatState):
    return state["active_intent"]


def chat_menu(state: ChatState):
    message = state["messages"][-1]
    menu_list = fetch_menu()
    menu = "\n".join(f"{item['name']} | {item['price']}" for item in menu_list) if menu_list else "No items available."

    response = LLM.invoke([
        CHAT_PROMPT,
        json.dumps({
            "conversation_history": [msg.content for msg in state["messages"]],
            "current_message": message.content,
            "menu_list": menu,
        })
    ]).content
    return {"messages": [AIMessage(content=response)]}


def chat_general(state: ChatState):
    message = state["messages"][-1]

    response = LLM.invoke([
        GENERAL_CHAT_PROMPT,
        json.dumps({
            "conversation_history": [msg.content for msg in state["messages"]],
            "current_message": message.content,
        })
    ]).content
    return {"messages": [AIMessage(content=response)]}


def book_order(state: ChatState):
    message = state["messages"][-1]
    menu_list = fetch_menu()
    items_available = [{"name": item["name"], "price": item["price"]} for item in menu_list] if menu_list else []

    response = LLM.invoke([
        BOOK_ORDER_PROMPT,
        json.dumps({
            "current_message": message.content,
            "conversation_history": [msg.content for msg in state["messages"]],
            "items_available": items_available,
        })
    ])

    try:
        parsed = sanitize_llm_json(response.content)
    except Exception as e:
        print(f"Error parsing JSON response: {e}")
        return {"messages": [AIMessage(content="I had trouble processing that. Could you try again?")]}

    if parsed["finalized"]:
        order = Order(
            phone_number=state["phone_number"],
            ordered_items=parsed["info"]["items"],
            status="Pending",
        )
        add_order_to_mongo(order)
        return {"messages": [AIMessage(content=f"{parsed['reply_for_user']}\nYour order token: {order.token}")]}

    return {"messages": [AIMessage(content=parsed["reply_for_user"])]}
