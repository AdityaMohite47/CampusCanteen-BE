import uuid, json, datetime, logging
from models import Message
from helper.mongo.mongo_helper import fetch_last_n_messages , get_last_message
from langchain_groq import ChatGroq
from helper.graph.prompts import SESSION_PROMPT
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
)
logger = logging.getLogger(__name__)


LLM = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

import re

def ask_ai_for_session(msgs: list[Message], msg: Message):
    conversation_history = ""
    if msgs:
        for previous_msg in msgs:
            conversation_history += f"{previous_msg.created_at} {previous_msg.sent_by}: {previous_msg.content}\n"
    else:
        conversation_history = "No previous messages."

    try:
        response = LLM.invoke([
            {"role": "system", "content": SESSION_PROMPT},
            {"role": "user", "content": json.dumps({
                "conversation_history": conversation_history,
                "current_message": msg.content
            })}
        ])

        cleaned = re.sub(r"^```(?:json)?|```$", "", response.content.strip(), flags=re.MULTILINE).strip()
        parsed_response = json.loads(cleaned)
        return parsed_response["new_session"]

    except Exception as e:
        print(f"Error asking LLM for session: {str(e)}")
        return False

def identify_session(msg: Message) -> str:

    last_msg = get_last_message(msg.phone_number)

    if not last_msg:
        new_session_id = str(uuid.uuid4())
        return new_session_id

    time_diff = (datetime.datetime.now() - last_msg.created_at).total_seconds()
    logger.info(f"Time difference between last and current message: {time_diff} seconds")

    if time_diff < 60:
        return last_msg.session_id

    last_10_msgs = fetch_last_n_messages(msg.phone_number)
    is_new_session = ask_ai_for_session(last_10_msgs, msg)

    if is_new_session:
        new_session_id = str(uuid.uuid4())
        return new_session_id

    return last_msg.session_id if last_msg else str(uuid.uuid4())


# for testing
# print(identify_session(Message(phone_number="1234567891", content="Hello", sent_by="user")))
# print(type(CHAIN))