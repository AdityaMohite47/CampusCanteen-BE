# CampusCanteen — Backend

AI-powered conversational food pre-ordering backend for campus canteens. Users interact via WhatsApp or any web chat interface; the system understands intent, manages session context, and places orders through an LLM-driven workflow.

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| API Server | FastAPI + Uvicorn |
| AI Workflow | LangGraph + LangChain |
| LLM | Groq — Llama 3.3 70B Versatile |
| Database | MongoDB |
| Validation | Pydantic |

## Project Structure

```
CampusCanteen-BE/
├── service.py          # FastAPI app — POST /message entry point
├── processor.py        # Core message processing pipeline
├── models.py           # Pydantic models: User, Message, SessionContext, Order
├── sample_menu.json    # Seed data for the Menu collection
├── test.py             # Interactive CLI for testing the bot
└── core/
    ├── llm.py          # LLM singletons (LLM temp=0.7, LLM_STRICT temp=0)
    ├── session.py      # Session continuity detection
    ├── context.py      # Session context retrieval and creation
    ├── graph/
    │   ├── graph.py    # LangGraph workflow definition
    │   ├── nodes.py    # Graph nodes: identify_intent, chat_intent, chat_menu, chat_general, book_order
    │   ├── prompts.py  # All LLM system prompts
    │   ├── state.py    # ChatState TypedDict
    │   └── utils.py    # JSON sanitization for LLM output
    └── db/
        ├── connection.py   # MongoDB singleton client
        └── crud.py         # All database operations
```

## LangGraph Workflow

```
identify_intent
    ├─→ chat_intent
    │       ├─→ chat_menu     (fetches menu, answers item/price queries)
    │       └─→ chat_general  (greetings, timings, pickup — no DB fetch)
    ├─→ book_order            (collects items, confirms, saves Order to DB)
    └─→ reply_unknown_intents (off-topic fallback)
```

## API

| Method | Path | Description |
|---|---|---|
| POST | `/message` | Send a user message, receive bot reply |
| GET | `/health` | Health check |

**Request body:**
```json
{
  "phone_number": "9876543210",
  "content": "What's on the menu?",
  "message_type": "text",
  "source": ""
}
```

## Environment Variables

Create a `.env` file in `CampusCanteen-BE/`:

```env
GROQ_API_KEY=

MONGO_USERNAME=root
MONGO_PASSWORD=root
MONGO_DATABASE=CampusCanteen
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_AUTH_SOURCE=admin

MESSAGES_COLLECTION=Messages
USERS_COLLECTION=Users
SESSIONS_COLLECTION=Sessions
ORDERS_COLLECTION=Orders
MENU_COLLECTION=Menu
```

## Setup & Run

```bash
# Install dependencies
pipenv install

# Seed the menu (run once)
mongoimport --uri "mongodb://root:root@localhost:27017/CampusCanteen?authSource=admin" \
  --collection Menu --file sample_menu.json --jsonArray

# Start the API server
pipenv run uvicorn service:app --reload --port 8000

# Or test interactively via CLI
pipenv run python test.py
```

## Demo

[![Campus Canteen Demo](https://img.youtube.com/vi/900mPHrd1K8/0.jpg)](https://youtu.be/900mPHrd1K8)
