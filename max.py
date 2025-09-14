import streamlit as st
import google.generativeai as genai
import json
import os
import uuid

st.set_page_config(page_title="Max by Debayan", page_icon="🧠", layout="wide")

# -------------------------
# Device-specific storage
# -------------------------
DEVICE_FOLDER = os.path.join(os.path.expanduser("~"), ".max_ai_data")
os.makedirs(DEVICE_FOLDER, exist_ok=True)

CHATS_FILE = os.path.join(DEVICE_FOLDER, "chats.json")

# Initialize chats file if missing
if not os.path.exists(CHATS_FILE):
    with open(CHATS_FILE, "w") as f:
        json.dump({}, f)

# -------------------------
# Load chats
# -------------------------
with open(CHATS_FILE, "r") as f:
    all_chats = json.load(f)

# -------------------------
# Session state
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# -------------------------
# Sidebar styling
# -------------------------
st.markdown("""
<style>
[data-testid="stSidebar"] {background-color: #141a22 !important; color: #f9fafb;}
[data-testid="stSidebar"] input, [data-testid="stSidebar"] textarea, [data-testid="stSidebar"] .stSelectbox select, [data-testid="stSidebar"] button {
    background-color: #141a22 !important; color: #f9fafb; border: 1px solid #374151;
}
[data-testid="stSidebar"] button:hover {background-color: #1e2530 !important;}
[data-testid="stSidebar"] .stTextInput>div>input, [data-testid="stSidebar"] .stTextArea>div>textarea {
    background-color: #141a22 !important; color: #f9fafb;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Main Chat UI
# -------------------------
USER_ID = "default_user"
if USER_ID not in all_chats:
    all_chats[USER_ID] = {}

user_chats = all_chats[USER_ID]

# Ensure at least one chat exists
if not user_chats:
    new_chat_id = str(uuid.uuid4())
    user_chats[new_chat_id] = {"title": "New Chat", "messages": []}

# Fix current chat id
if st.session_state.current_chat_id not in user_chats:
    st.session_state.current_chat_id = list(user_chats.keys())[0]

selected_chat_id = st.sidebar.selectbox(
    "Select a chat:",
    options=list(user_chats.keys()),
    index=list(user_chats.keys()).index(st.session_state.current_chat_id),
    format_func=lambda cid: user_chats[cid]["title"]
)
st.session_state.current_chat_id = selected_chat_id

# Safely assign messages
st.session_state.messages = user_chats.get(selected_chat_id, {"messages": []})["messages"]

# New chat
if st.sidebar.button("✒️ New Chat"):
    new_chat_id = str(uuid.uuid4())
    user_chats[new_chat_id] = {"title": "New Chat", "messages": []}
    st.session_state.current_chat_id = new_chat_id
    st.session_state.messages = []

# Edit chat title
new_title = st.sidebar.text_input("Edit Chat Title:", value=user_chats[selected_chat_id]["title"])
if new_title != user_chats[selected_chat_id]["title"]:
    user_chats[selected_chat_id]["title"] = new_title

# Delete chat
if st.sidebar.button("🧢 Delete Selected Chat"):
    if selected_chat_id in user_chats:
        del user_chats[selected_chat_id]
        if user_chats:
            st.session_state.current_chat_id = list(user_chats.keys())[0]
            st.session_state.messages = user_chats[st.session_state.current_chat_id]["messages"]
        else:
            new_chat_id = str(uuid.uuid4())
            user_chats[new_chat_id] = {"title": "New Chat", "messages": []}
            st.session_state.current_chat_id = new_chat_id
            st.session_state.messages = []

# Save chats helper
def save_chats():
    with open(CHATS_FILE, "w") as f:
        json.dump(all_chats, f)

st.html("<center><h1 style='font-size:60px;'>Max 🧠</h1></center>")

genai.configure(api_key="YOUR_API_KEY_HERE")
text_model = genai.GenerativeModel("gemini-2.0-flash")

intro_placeholder = st.empty()
if len(st.session_state.messages) == 0:
    intro_placeholder.markdown(
        "<div style='display: flex; justify-content: center; align-items: center; height: 65vh; font-size: 3rem; font-weight: bold; color: white; opacity: 0.5;'>Hello!</div>",
        unsafe_allow_html=True
    )

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])

prompt = st.chat_input("Type here...")
if prompt:
    intro_placeholder.empty()
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    if user_chats[selected_chat_id]["title"] == "New Chat" and prompt:
        user_chats[selected_chat_id]["title"] = prompt[:30]

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
    user_chats[selected_chat_id]["messages"] = st.session_state.messages
    save_chats()
