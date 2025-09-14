import streamlit as st
import google.generativeai as genai
import json
import os
import uuid
import platform

st.set_page_config(page_title="Max by Debayan", page_icon="🧠", layout="wide")

# -------------------------
# Device-specific storage
# -------------------------
# Use platform.node() or platform.system() + USER to make it device/browser specific
DEVICE_ID = platform.node()  # unique per machine
DEVICE_FOLDER = os.path.join(os.path.expanduser("~"), f".max_ai_data_{DEVICE_ID}")
os.makedirs(DEVICE_FOLDER, exist_ok=True)

CHATS_FILE = os.path.join(DEVICE_FOLDER, "chats.json")

# Initialize chats file if missing
if not os.path.exists(CHATS_FILE):
    with open(CHATS_FILE, "w") as f:
        json.dump({}, f)

# Load chats
with open(CHATS_FILE, "r") as f:
    chats = json.load(f)

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# Ensure at least one chat exists
if not chats:
    new_chat_id = str(uuid.uuid4())
    chats[new_chat_id] = {"title": "New Chat", "messages": []}

# Fix current chat id
if st.session_state.current_chat_id not in chats:
    st.session_state.current_chat_id = list(chats.keys())[0]

# Safe selection of current chat
selected_chat_id = st.sidebar.selectbox(
    "Select a chat:",
    options=list(chats.keys()),
    index=list(chats.keys()).index(st.session_state.current_chat_id),
    format_func=lambda cid: chats[cid].get("title", "New Chat")
)
st.session_state.current_chat_id = selected_chat_id
current_chat = chats.get(selected_chat_id, {"title": "New Chat", "messages": []})
st.session_state.messages = current_chat.get("messages", [])

# Sidebar buttons
if st.sidebar.button("✒️ New Chat"):
    new_chat_id = str(uuid.uuid4())
    chats[new_chat_id] = {"title": "New Chat", "messages": []}
    st.session_state.current_chat_id = new_chat_id
    st.session_state.messages = []

# Edit chat title safely
new_title = st.sidebar.text_input("Edit Chat Title:", value=current_chat.get("title", "New Chat"))
if new_title != current_chat.get("title", "New Chat"):
    current_chat["title"] = new_title
    chats[selected_chat_id] = current_chat

# Delete chat safely
if st.sidebar.button("🧢 Delete Selected Chat"):
    if selected_chat_id in chats:
        del chats[selected_chat_id]
        if chats:
            st.session_state.current_chat_id = list(chats.keys())[0]
            st.session_state.messages = chats[st.session_state.current_chat_id]["messages"]
        else:
            new_chat_id = str(uuid.uuid4())
            chats[new_chat_id] = {"title": "New Chat", "messages": []}
            st.session_state.current_chat_id = new_chat_id
            st.session_state.messages = []

# Save chats helper
def save_chats():
    with open(CHATS_FILE, "w") as f:
        json.dump(chats, f)

st.html("<center><h1 style='font-size:60px;'>Max 🧠</h1></center>")

# Configure Gemini
genai.configure(api_key="AIzaSyALrcQnmp18z2h2ParAb6PXimCpN0HxX8Y")
text_model = genai.GenerativeModel("gemini-2.0-flash")

# Intro
intro_placeholder = st.empty()
if len(st.session_state.messages) == 0:
    intro_placeholder.markdown(
        "<div style='display: flex; justify-content: center; align-items: center; height: 65vh; font-size: 3rem; font-weight: bold; color: white; opacity: 0.5;'>Hello!</div>",
        unsafe_allow_html=True
    )

# Display previous messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Chat input
prompt = st.chat_input("Type here...")
if prompt:
    intro_placeholder.empty()
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if current_chat.get("title", "New Chat") == "New Chat" and prompt:
        current_chat["title"] = prompt[:30]

    all_messages_text = ""
    for m in st.session_state.messages:
        all_messages_text += f"{m['role'].capitalize()}: {m['content']}\n"

    with st.spinner("Thinking..."):
        try:
            reply = text_model.generate_content(all_messages_text).text
        except Exception as e:
            reply = f"Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)
    current_chat["messages"] = st.session_state.messages
    chats[selected_chat_id] = current_chat
    save_chats()
