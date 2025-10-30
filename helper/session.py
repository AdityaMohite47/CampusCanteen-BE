import uuid, json, datetime
from models import Message
from langchain.prompts import PromptTemplate
from helper.mongo.mongo_helper import fetch_last_n_messages , get_last_message
from langchain_google_genai import ChatGoogleGenerativeAI
import dotenv

dotenv.load_dotenv()


LLM = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)


PROMPT = PromptTemplate(
        input_variables=["conversation_history", "current_message"],
        template="""
            Your job is to decide if the user's latest message starts a **new conversation session** or continues an **existing session**. 
            You will receive the last few messages between the user and the assistant, along with the user's latest message. 
            These messages are in order from oldest to newest.
            
            Use the following criteria to make your decision:
            WHEN TO MARK AS A NEW SESSION:
            - The user starts with a greeting like "Hi", "Hello", etc.
            - The message clearly introduces a new topic, unrelated to recent messages.
            - There has been a long gap since the last message.
            - The previous session seems to have ended and a fresh interaction is beginning.

            WHEN TO MARK AS AN ONGOING SESSION:
            - The user continues talking about the same topic as before.
            - The user is replying to something the assistant recently asked.
            - The assistant is guiding the user through a multi-step process, and the user responds with details or clarifications.
            - The message connects clearly to recent ones in flow or context.

            NOTE:
            - Consider both the time gap and the topical change when deciding.


            You must respond in this exact format:
            {{"new_session": true/false}}

            Input:  

            Conversation History:
            {conversation_history}

            Current User Message:
            {current_message}

            Analyze carefully and return the output.

            """
    )

CHAIN = PROMPT | LLM

import re

def ask_ai_for_session(msgs: list[Message], msg: Message):
    conversation_history = ""
    if msgs:
        for previous_msg in msgs:
            conversation_history += f"{previous_msg.created_at} {previous_msg.sent_by}: {previous_msg.content}\n"
    else:
        conversation_history = "No previous messages."

    try:
        response = CHAIN.invoke({
            "conversation_history": conversation_history,
            "current_message": msg.content
        })

        # 🧽 Clean up markdown if needed
        cleaned = re.sub(r"^```(?:json)?|```$", "", response.content.strip(), flags=re.MULTILINE).strip()
        parsed_response = json.loads(cleaned)
        return parsed_response["new_session"]
    except Exception as e:
        print(f"Error asking LLM for session: {str(e)}")
        return False



def identify_session(msg: Message) -> str:
    """
    Identify the session for the given message.
    If last message is under a minute ago, continue the same session.
    Otherwise, ask the AI to determine if it's a new session or not.

    Returns:
        str: session_id to use for this message
    """

    last_msg = get_last_message(msg.student_id)

    if not last_msg:
        new_session_id = str(uuid.uuid4())
        return new_session_id

    time_diff = (datetime.datetime.now() - last_msg.created_at).total_seconds()
    # Message is fresh — continue current session
    if time_diff < 60:
        return last_msg.session_id

    # Ask AI if new session is needed
    last_10_msgs = fetch_last_n_messages(msg.student_id)
    is_new_session = ask_ai_for_session(last_10_msgs, msg)

    if is_new_session:
        new_session_id = str(uuid.uuid4())
        return new_session_id

    return last_msg.session_id if last_msg else str(uuid.uuid4())