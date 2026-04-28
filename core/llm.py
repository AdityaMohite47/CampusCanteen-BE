from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# For chat/creative responses
LLM = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)

# For structured/JSON responses requiring 
LLM_STRICT = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)