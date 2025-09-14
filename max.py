import streamlit as st
import google.generativeai as genai
import json
import os
import hashlib
import uuid

st.set_page_config(page_title="Max by Debayan", page_icon="🧠", layout="wide")

DEVICE_FOLDER = "device_data"
if not os.path.exists(DEVICE_FOLDER):
    os.makedirs(DEVICE_FOLDER)

ACCOUNTS_FILE = os.path.join(DEVICE_FOLDER, "accounts.json")
CHATS_FILE = os.path.join(DEVICE_FOLDER, "chats.json")
CURRENT_USER_FILE = os.path.join(DEVICE_FOLDER, "current_user.json")

for file_path, default in [(ACCOUNTS_FILE, {}), (CHATS_FILE, {}), (CURRENT_USER_FILE, {})]:
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump(default, f)

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

if "user_email" not in st.session_state:
    st.session_state.user_email = current_user_data.get("user_email")
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

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

# ... keep the rest of your chat UI code exactly the same, just replace previous global files with these device-specific files ...
