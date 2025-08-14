import streamlit as st
import google.generativeai as genai
import hashlib
import json
from pathlib import Path
from streamlit_oauth import OAuth2Component

# -------------------
# CONFIG
# -------------------
st.set_page_config(page_title="Max-AI by Debayan", page_icon="🧠")

DATA_FILE = "data.txt"

# -------------------
# LOAD USERS
# -------------------
def load_users():
    if Path(DATA_FILE).exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"users": [], "openai_keys": [], "google_users": []}

def save_users(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

# -------------------
# LOGIN SYSTEM
# -------------------
users_data = load_users()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None

def login_username_password():
    st.subheader("Login with Username & Password")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        for u in users_data["users"]:
            if u["username"] == username and u["password"] == hash_pw(password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success(f"Welcome {username}")
                return
        st.error("Invalid credentials")

def login_openai():
    st.subheader("Login with OpenAI API Key")
    key = st.text_input("Enter your OpenAI API Key", type="password")
    if st.button("Login with OpenAI"):
        if key in users_data["openai_keys"]:
            st.session_state.authenticated = True
            st.session_state.username = "OpenAI_User"
            st.success("OpenAI login successful")
        else:
            st.error("Invalid API Key")

def login_google():
    st.subheader("Login with Google")
    client_id = "YOUR_GOOGLE_CLIENT_ID"
    client_secret = "YOUR_GOOGLE_CLIENT_SECRET"
    redirect_uri = "http://localhost:8501"
    oauth2 = OAuth2Component(client_id, client_secret, "https://accounts.google.com/o/oauth2/auth", "https://oauth2.googleapis.com/token")
    auth_url = oauth2.authorize_url(redirect_uri, scope="openid email profile", state="random_state")
    st.markdown(f"[Login with Google]({auth_url})")

# -------------------
# SHOW LOGIN OPTIONS
# -------------------
if not st.session_state.authenticated:
    st.title("Login to Max-AI")
    method = st.radio("Choose Login Method", ["Username & Password", "OpenAI Key", "Google Login"])
    if method == "Username & Password":
        login_username_password()
    elif method == "OpenAI Key":
        login_openai()
    elif method == "Google Login":
        login_google()
else:
    # -------------------
    # MAIN CHAT APP
    # -------------------
    genai.configure(api_key="AIzaSyALrcQnmp16z2h2ParAb6PXimCpN0HxX8Y")
    text_model = genai.GenerativeModel("gemini-2.0-flash")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    prompt = st.chat_input("Type here...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        reply = text_model.generate_content(prompt).text
        st.session_state.messages.append({"role": "assistant", "content": reply})

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
