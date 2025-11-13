import streamlit as st
import asyncio
from models import Message
from processor import process_message

st.set_page_config(page_title="CampusCanteen", layout="centered")

# ---- SESSION STATE ----
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---- Heading ----
st.markdown("<h1 style='text-align:center;'>CampusCanteen</h1>", unsafe_allow_html=True)
st.write("Preorder meals by chatting with the assistant below.")
st.write("---")

# ---- Display chat history ----
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# ---- User input ----
user_input = st.chat_input("Type your message...")

if user_input:
    # Store user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)

    # ---- Call LangGraph backend ----
    try:
        msg = Message(
            phone_number="TEST",     # fixed, no prompt needed
            content=user_input,
            sent_by="student"
        )

        # run async function safely in Streamlit
        bot_reply = asyncio.run(process_message(msg))

    except Exception as e:
        bot_reply = f"Error: {e}"

    # Store and show bot reply
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    st.chat_message("assistant").markdown(bot_reply)