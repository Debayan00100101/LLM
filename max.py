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

# --- Initialize files ---
for file_path, default in [(ACCOUNTS_FILE, {}), (CHATS_FILE, {})]:
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump(default, f)

# --- Load data ---
with open(ACCOUNTS_FILE, "r") as f:
    accounts = json.load(f)
with open(CHATS_FILE, "r") as f:
    all_chats = json.load(f)

# --- Password hashing ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- Save functions ---
def save_accounts():
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f)

def save_chats():
    with open(CHATS_FILE, "w") as f:
        json.dump(all_chats, f)

# --- Session state ---
if "user_email" not in st.session_state:
    st.session_state.user_email = None
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

# --- Authentication functions ---
def login_user(email, password):
    if email in accounts and accounts[email]["password"] == hash_password(password):
        st.session_state.user_email = email
        if email not in all_chats:
            all_chats[email] = {}
        st.session_state.messages = []
        st.session_state.current_chat_id = None
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
    return True, email

# --- Login/Register interface ---
if st.session_state.user_email is None:
    st.title("Max-AI Login / Registration")

    tab = st.radio("Choose Action:", ["Login", "Register"])

    if tab == "Login":
        email_input = st.text_input("Email")
        password_input = st.text_input("Password", type="password")
        if st.button("Login"):
            if login_user(email_input, password_input):
                st.success(f"Logged in as {accounts[email_input]['username']}")
                st.write("Rerun to chat")
            else:
                st.error("Invalid email or password!")

    elif tab == "Register":
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        if st.button("Register"):
            success, msg = register_user(username_input, password_input)
            if success:
                # Automatically log in after registration
                st.session_state.user_email = msg
                st.session_state.messages = []
                st.session_state.current_chat_id = None
                st.success(f"Account created and logged in! Welcome, {username_input}")
                
            else:
                st.error(msg)

# --- Main Chat Page ---
else:
    user_email = st.session_state.user_email
    st.sidebar.title(f"Chats - {accounts[user_email]['username']}")

    user_chats = all_chats[user_email]

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
        del accounts[user_email]
        del all_chats[user_email]
        save_accounts()
        save_chats()
        st.session_state.user_email = None
        st.session_state.messages = []
        st.session_state.current_chat_id = None
        st.success("Account deleted. You can now register or login.")
        

    # --- Main Chat UI ---
    st.html("<center><h1 style='font-size:60px;'>Max 🧠</h1></center>")

    # --- Configure AI ---
    genai.configure(api_key="AIzaSyALrcQnmp18z2h2ParAb6PXimCpN0HxX8Y")
    text_model = genai.GenerativeModel("gemini-2.0-flash")

    intro_placeholder = st.empty()
    if len(st.session_state.messages) == 0:
        intro_placeholder.markdown(
            f"<div style='display: flex; justify-content: center; align-items: center; height: 65vh; font-size: 3rem; font-weight: bold; color: white; opacity: 0.5;'>Hello, {accounts[user_email]['username']}!</div>",
            unsafe_allow_html=True
        )

    # --- Display messages ---
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user",avatar="https://wallpapercave.com/wp/wp9110432.jpg").write(msg["content"])
        else:
            st.chat_message("assistant",avatar="https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg").write(msg["content"])

    # --- Chat input ---
    prompt = st.chat_input("Type here...")
    if prompt:
        intro_placeholder.empty()
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user",avatar="https://wallpapercave.com/wp/wp9110432.jpg").write(prompt)
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
        st.chat_message("assistant",avatar="https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg").write(reply)
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





