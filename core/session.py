import uuid, json, datetime, logging, re
from models import Message
from core.db.crud import fetch_last_n_messages, get_last_message
from core.llm import LLM_STRICT
from core.graph.prompts import SESSION_PROMPT
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


def ask_ai_for_session(msgs: list[Message], msg: Message) -> bool:
    if msgs:
        conversation_history = "".join(
            f"{m.created_at} {m.sent_by}: {m.content}\n" for m in msgs
        )
    else:
        conversation_history = "No previous messages."

    try:
        response = LLM_STRICT.invoke([
            {"role": "system", "content": SESSION_PROMPT},
            {"role": "user", "content": json.dumps({
                "conversation_history": conversation_history,
                "current_message": msg.content
            })}
        ])
        cleaned = re.sub(r"^```(?:json)?|```$", "", response.content.strip(), flags=re.MULTILINE).strip()
        return json.loads(cleaned)["new_session"]
    except Exception as e:
        logger.error(f"Error asking LLM for session: {e}")
        return False


def identify_session(msg: Message) -> str:
    last_msg = get_last_message(msg.phone_number)

    if not last_msg:
        return str(uuid.uuid4())

    time_diff = (datetime.datetime.now() - last_msg.created_at).total_seconds()
    logger.info(f"Time since last message: {time_diff:.1f}s")

    if time_diff < 60:
        return last_msg.session_id

    last_10_msgs = fetch_last_n_messages(msg.phone_number)
    if ask_ai_for_session(last_10_msgs, msg):
        return str(uuid.uuid4())

    return last_msg.session_id
