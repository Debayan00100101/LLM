import streamlit as st
import google.generativeai as genai
import json
import os
import hashlib
import uuid

st.set_page_config(page_title="Max by Debayan", page_icon="🧠", layout="wide")

# --- Files ---
ACCOUNTS_FILE = "accounts.json"
CHATS_FILE = "all_chats.json"
DEVICE_FILE = "device_id.json"
LAST_USER_FILE = "last_user.json"

# --- Initialize files ---
for file_path, default in [(ACCOUNTS_FILE, {}), (CHATS_FILE, {})]:
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump(default, f)

with open(ACCOUNTS_FILE, "r") as f:
    accounts = json.load(f)
with open(CHATS_FILE, "r") as f:
    all_chats = json.load(f)

# --- Generate/Get unique device ID ---
def get_device_id():
    if os.path.exists(DEVICE_FILE):
        with open(DEVICE_FILE, "r") as f:
            return json.load(f).get("device_id")
    else:
        device_id = str(uuid.uuid4())
        with open(DEVICE_FILE, "w") as f:
            json.dump({"device_id": device_id}, f)
        return device_id

device_id = get_device_id()

# --- Password hashing ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- Save functions ---
def save_accounts():
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f)

def save_last_user(email):
    with open(LAST_USER_FILE, "w") as f:
        json.dump({"email": email, "device_id": device_id}, f)

def get_last_user():
    if os.path.exists(LAST_USER_FILE):
        with open(LAST_USER_FILE, "r") as f:
            data = json.load(f)
            if data.get("device_id") == device_id:
                return data.get("email")
    return None

def save_chats():
    with open(CHATS_FILE, "w") as f:
        json.dump(all_chats, f)

# --- Session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# --- Sidebar styling ---
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

# --- Check last user for this device ---
registered_email = get_last_user()

# --- Registration / login ---
if registered_email is None:
    st.title("Max-AI Registration System (Device-Specific)")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        if not username or not password:
            st.error("Enter both username and password!")
        else:
            email = f"{username}@max.com"
            if email in accounts:
                st.error("Username already taken!")
            else:
                # Create account for this device
                accounts[email] = {"password": hash_password(password), "username": username}
                save_accounts()
                save_last_user(email)
                st.success(f"Account created for this device! Email: {email}")
else:
    st.sidebar.title("Chats")
    if registered_email not in all_chats:
        all_chats[registered_email] = {}
    user_chats = all_chats[registered_email]

    # --- New chat ---
    if st.sidebar.button("✒️ New Chat"):
        new_chat_id = str(uuid.uuid4())
        user_chats[new_chat_id] = {"title": "New Chat", "messages": []}
        save_chats()
        st.session_state.current_chat_id = new_chat_id
        st.session_state.messages = []

    # --- Select chat ---
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

    # --- Edit chat title ---
    new_title = st.sidebar.text_input("Edit Chat Title:", value=user_chats[selected_chat_id]["title"])
    if new_title != user_chats[selected_chat_id]["title"]:
        user_chats[selected_chat_id]["title"] = new_title
        save_chats()

    # --- Delete chat ---
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

    # --- Delete account ---
    if st.sidebar.button("⚠️ Delete Account"):
        if registered_email in accounts:
            del accounts[registered_email]
        if registered_email in all_chats:
            del all_chats[registered_email]
        save_accounts()
        save_chats()
        if os.path.exists(LAST_USER_FILE):
            os.remove(LAST_USER_FILE)
        st.success("Account deleted! You can now create an account on this device.")
        st.stop()

    # --- Main Chat UI ---
    st.html("<h1 style='font-size:60px;'>Max 🧠</h1>")

    # Configure AI
    genai.configure(api_key="YOUR_API_KEY_HERE")
    text_model = genai.GenerativeModel("gemini-2.0-flash")

    intro_placeholder = st.empty()
    if len(st.session_state.messages) == 0:
        intro_placeholder.markdown(
            f"<div style='display: flex; justify-content: center; align-items: center; height: 65vh; font-size: 3rem; font-weight: bold; color: white; opacity: 0.5;'>Hello, {accounts[registered_email]['username']}!</div>",
            unsafe_allow_html=True
        )

    # --- Display messages ---
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user", avatar="https://wallpapercave.com/wp/wp9110432.jpg").write(msg["content"])
        else:
            st.chat_message("assistant", avatar="https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg").write(msg["content"])

    # --- Chat input ---
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
        if selected_chat_id:
            user_chats[selected_chat_id]["messages"] = st.session_state.messages
            save_chats()

    # --- Footer ---
    st.markdown("""
    <style>
        .footer {position: fixed; left: 0; bottom: 0; width: 100%; background-color: #1f2937; color: #f9fafb; text-align: center; padding: 0.75rem 0; font-size: 0.875rem; opacity: 0.85; border-top: 1px solid #374151;}
        .footer a {color: #3b82f6; text-decoration: underline;}
    </style>
    <div class="footer">Max can make mistakes. Please verify important information. See <a href="#">Cookie Preferences</a>.</div>
    """, unsafe_allow_html=True)
