import streamlit as st
import google.generativeai as genai
import json
import os
import hashlib
import uuid
import platform

st.set_page_config(page_title="Max by Debayan", page_icon="🧠", layout="wide")

# Use a unique device folder based on machine identifier
DEVICE_ID = platform.node()  # Unique per machine
DEVICE_FOLDER = f"device_data_{DEVICE_ID}"
os.makedirs(DEVICE_FOLDER, exist_ok=True)

ACCOUNTS_FILE = os.path.join(DEVICE_FOLDER, "accounts.json")
CHATS_FILE = os.path.join(DEVICE_FOLDER, "chats.json")
CURRENT_USER_FILE = os.path.join(DEVICE_FOLDER, "current_user.json")

for file_path, default in [(ACCOUNTS_FILE, {}), (CHATS_FILE, {}), (CURRENT_USER_FILE, {})]:
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump(default, f)

# Load files
with open(ACCOUNTS_FILE, "r") as f:
    accounts = json.load(f)
with open(CHATS_FILE, "r") as f:
    all_chats = json.load(f)
with open(CURRENT_USER_FILE, "r") as f:
    current_user_data = json.load(f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_accounts():
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f)

def save_chats():
    with open(CHATS_FILE, "w") as f:
        json.dump(all_chats, f)

def save_current_user():
    with open(CURRENT_USER_FILE, "w") as f:
        json.dump(current_user_data, f)

# Session state
stored_email = current_user_data.get("user_email")
if stored_email and stored_email in accounts:
    st.session_state.user_email = stored_email
else:
    st.session_state.user_email = None
    if "user_email" in current_user_data:
        del current_user_data["user_email"]
        save_current_user()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# Sidebar styling
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

# Authentication
def login_user(email, password):
    if email in accounts and accounts[email]["password"] == hash_password(password):
        st.session_state.user_email = email
        if email not in all_chats:
            all_chats[email] = {}
        st.session_state.messages = []
        st.session_state.current_chat_id = None
        current_user_data["user_email"] = email
        save_current_user()
        return True
    return False

def register_user(username, password):
    email = f"{username}@max.com"
    if email in accounts:
        return False, "Username already exists!"
    accounts[email] = {"username": username, "password": hash_password(password)}
    all_chats[email] = {}
    save_accounts()
    save_chats()
    st.session_state.user_email = email
    st.session_state.messages = []
    st.session_state.current_chat_id = None
    current_user_data["user_email"] = email
    save_current_user()
    return True, email

# Login/Register interface
if st.session_state.user_email is None:
    st.title("Max-AI Login / Registration")
    tab = st.radio("Choose Action:", ["Login", "Register"])

    if tab == "Login":
        email_input = st.text_input("Email")
        password_input = st.text_input("Password", type="password")
        if st.button("Login"):
            if login_user(email_input, password_input):
                st.success(f"Logged in as {accounts[email_input]['username']}")
            else:
                st.error("Invalid email or password!")

    elif tab == "Register":
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        if st.button("Register"):
            success, msg = register_user(username_input, password_input)
            if success:
                st.success(f"Account created and logged in! Welcome, {username_input}")
            else:
                st.error(msg)

# Main Chat
else:
    user_email = st.session_state.user_email
    st.sidebar.title(f"Chats - {accounts[user_email]['username']}")
    user_chats = all_chats[user_email]

    if st.sidebar.button("✒️ New Chat"):
        new_chat_id = str(uuid.uuid4())
        user_chats[new_chat_id] = {"title": "New Chat", "messages": []}
        save_chats()
        st.session_state.current_chat_id = new_chat_id
        st.session_state.messages = []

    chat_ids = list(user_chats.keys())
    if not chat_ids:
        new_chat_id = str(uuid.uuid4())
        user_chats[new_chat_id] = {"title": "New Chat", "messages": []}
        save_chats()
        chat_ids = list(user_chats.keys())

    if st.session_state.current_chat_id not in chat_ids:
        st.session_state.current_chat_id = chat_ids[0]

    selected_chat_id = st.sidebar.selectbox(
        "Select a chat:", chat_ids,
        index=chat_ids.index(st.session_state.current_chat_id),
        format_func=lambda cid: user_chats[cid]["title"]
    )
    st.session_state.current_chat_id = selected_chat_id
    st.session_state.messages = user_chats[selected_chat_id]["messages"]

    new_title = st.sidebar.text_input("Edit Chat Title:", value=user_chats[selected_chat_id]["title"])
    if new_title != user_chats[selected_chat_id]["title"]:
        user_chats[selected_chat_id]["title"] = new_title
        save_chats()

    if st.sidebar.button("🧢 Delete Selected Chat"):
        if selected_chat_id in user_chats:
            del user_chats[selected_chat_id]
            save_chats()
            if user_chats:
                st.session_state.current_chat_id = list(user_chats.keys())[0]
                st.session_state.messages = user_chats[st.session_state.current_chat_id]["messages"]
            else:
                new_chat_id = str(uuid.uuid4())
                user_chats[new_chat_id] = {"title": "New Chat", "messages": []}
                save_chats()
                st.session_state.current_chat_id = new_chat_id
                st.session_state.messages = []

    if st.sidebar.button("⚠️ Delete Account"):
        del accounts[user_email]
        del all_chats[user_email]
        save_accounts()
        save_chats()
        if "user_email" in current_user_data:
            del current_user_data["user_email"]
            save_current_user()
        st.session_state.user_email = None
        st.session_state.messages = []
        st.session_state.current_chat_id = None
        st.success("Account deleted. You can now register or login.")

    st.html("<center><h1 style='font-size:60px;'>Max 🧠</h1></center>")

    genai.configure(api_key="YOUR_API_KEY_HERE")
    text_model = genai.GenerativeModel("gemini-2.0-flash")

    intro_placeholder = st.empty()
    if len(st.session_state.messages) == 0:
        intro_placeholder.markdown(
            f"<div style='display: flex; justify-content: center; align-items: center; height: 65vh; font-size: 3rem; font-weight: bold; color: white; opacity: 0.5;'>Hello, {accounts[user_email]['username']}!</div>",
            unsafe_allow_html=True
        )

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user", avatar="https://wallpapercave.com/wp/wp9110432.jpg").write(msg["content"])
        else:
            st.chat_message("assistant", avatar="https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg").write(msg["content"])

    prompt = st.chat_input("Type here...")
    if prompt:
        intro_placeholder.empty()
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user", avatar="https://wallpapercave.com/wp/wp9110432.jpg").write(prompt)
        if user_chats[selected_chat_id]["title"] == "New Chat" and prompt:
            user_chats[selected_chat_id]["title"] = prompt[:30]

        all_messages_text = ""
        for cid, chat in user_chats.items():
            for m in chat["messages"]:
                all_messages_text += f"{m['role'].capitalize()}: {m['content']}\n"
        all_messages_text += f"User: {prompt}\n"

        with st.spinner("Thinking..."):
            try:
                reply = text_model.generate_content(all_messages_text).text
            except Exception as e:
                reply = f"Error: {e}"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant", avatar="https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg").write(reply)
        user_chats[selected_chat_id]["messages"] = st.session_state.messages
        save_chats()

    st.markdown("""
    <style>
        .footer {position: fixed; left: 0; bottom: 0; width: 100%; background-color: #1f2937; color: #f9fafb; text-align: center; padding: 0.75rem 0; font-size: 0.875rem; opacity: 0.85; border-top: 1px solid #374151;}
        .footer a {color: #3b82f6; text-decoration: underline;}
    </style>
    <div class="footer">Max can make mistakes. Please verify important information. See <a href="#">Cookie Preferences</a>.</div>
    """, unsafe_allow_html=True)
