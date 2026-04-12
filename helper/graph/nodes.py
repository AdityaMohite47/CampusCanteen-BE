import random, json
from helper.graph.chat_state import ChatState
from langchain_core.messages import AIMessage
from helper.llm import LLM
from helper.graph.prompts import *
from helper.mongo.mongo_helper import add_order_to_mongo, fetch_menu
from helper.graph.utils import sanitize_llm_json
from models import Order
    
def reply_unknown_intents(state:ChatState):
    fallback_responses = [
        "I'm here to help with canteen-related questions. You can ask about today’s menu, booking food, or payment options! 🍴",
        "I specialize in food ordering help! If you’re looking for the menu or want to prebook a meal, I’ve got you covered ✅",
        "Oops! That’s a bit outside my zone. Try asking about menu items, booking your meal, or payment methods 🚫",
        "I'm focused on helping you order from the canteen. Want to check the menu or place a prebook order? 📋",
        "That sounds interesting! But my focus is on food ordering, payments, and helping you with your canteen orders 🔄"
    ]
    reply = random.choice(fallback_responses)
    return {"messages": [AIMessage(content=reply)]} 


def identify_intent(state:ChatState):
    message = state["messages"][-1]

    try:
        intent = LLM.invoke([
            INTENT_PROMPT , 
            json.dumps({
                "conversation_history": [msg.content for msg in state["messages"]],
                "current_message": message.content
            })
        ])
    except Exception as e:
        print("ERROR IDENTIFYING INTENT: " + str(e))
        return 
    
    return {"active_intent": intent.content}

def intent_router(state:ChatState):
    print(state["active_intent"])
    return state["active_intent"]

def Chat(state:ChatState):
    message = state["messages"][-1]
    menu_list = fetch_menu()

    menu = ""
    if menu_list:
        menu = "\n".join(
            f"{item['name']} | {item['price']}" for item in menu_list
        )
    else:
        menu = "No Vendors avaliable."

    response = LLM.invoke([
        CHAT_PROMPT, 
        json.dumps({
            "conversation_history": [msg.content for msg in state["messages"]],
            "current_message": message.content,
            "menu_list": menu
        })
    ]).content

    return {'messages':[AIMessage(content=response)]}
       
    
def book_order(state:ChatState):
    message = state["messages"][-1]

    response = LLM.invoke([
        BOOK_ORDER_PROMPT,
        json.dumps({
            "Current_Message": message.content,
            "Conversation_History" : [msg.content for msg in state["messages"]]
            }
        )
    ])

    try:
        parsed_response = sanitize_llm_json(response.content)
    except Exception as e:
        print("Error parsing JSON response: " , e)
        return {"messages": [AIMessage(content="I had trouble processing that. Let me try again.")]}
    
    if parsed_response["finalized"]:
        order_object = Order(
            phone_number=state["phone_number"],
            ordered_items=[
                item for item in parsed_response["info"]["items"]
            ],
            status="Pending",
        )
        add_order_to_mongo(order_object)
        return {"messages":[AIMessage(content=parsed_response['reply_for_user'] + f"\n Token Number for Your Order is : {order_object.token}")]}

    return {"messages":[AIMessage(content=parsed_response['reply_for_user'])]}

# json
# {
#   "reply_for_user": "Got it! 10 Veg Rolls for you. How would you like to pay – online with QR or at the canteen?",
#   "finalized": false,
#   "info": {
#     "items": [
#       {
#         "name": "Veg Roll",
#         "quantity": "10"
#       }
#     ],
#     "payment_method": null
#   }
# }