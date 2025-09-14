import streamlit as st
import google.generativeai as genai
import json
import os
import hashlib
import uuid

# Try to use browser cookies for per-device persistence.
# If the library isn't installed, we fall back to a server-side device file (which will be shared
# when the app is hosted centrally). For true per-device (browser) persistence, install:
# pip install streamlit-cookies-manager
try:
    from streamlit_cookies_manager import EncryptedCookieManager
    COOKIE_MANAGER_AVAILABLE = True
except Exception:
    COOKIE_MANAGER_AVAILABLE = False

st.set_page_config(page_title="Max by Debayan", page_icon="🧠", layout="wide")

ACCOUNTS_FILE = "accounts.json"
CHATS_FILE = "all_chats.json"
DEVICE_FILE = "device_last_user.json"  # fallback only

# --- Initialize files ---
if not os.path.exists(ACCOUNTS_FILE):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump({}, f)
if not os.path.exists(CHATS_FILE):
    with open(CHATS_FILE, "w") as f:
        json.dump({}, f)

with open(ACCOUNTS_FILE, "r") as f:
    accounts = json.load(f)
with open(CHATS_FILE, "r") as f:
    all_chats = json.load(f)

# --- Cookie manager setup ---
if COOKIE_MANAGER_AVAILABLE:
    cookies = EncryptedCookieManager(prefix="max_ai_")
    # cookies.ready() must be true before reading/writing cookies
    if not cookies.ready():
        # stop here so the cookie manager can initialize; the component will re-run when ready
        st.stop()

# --- Helpers ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_accounts():
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f)

def save_chats():
    with open(CHATS_FILE, "w") as f:
        json.dump(all_chats, f)

# --- Last-user persistence (per-device) ---
if COOKIE_MANAGER_AVAILABLE:
    def save_last_user(email):
        cookies["last_user"] = email
        cookies.save()

    def get_last_user():
        return cookies.get("last_user", None)

    def clear_last_user():
        if "last_user" in cookies:
            del cookies["last_user"]
            cookies.save()
else:
    # Fallback: server-side device file (not recommended if app is hosted centrally)
    def save_last_user(email):
        with open(DEVICE_FILE, "w") as f:
            json.dump({"email": email}, f)

    def get_last_user():
        if os.path.exists(DEVICE_FILE):
            with open(DEVICE_FILE, "r") as f:
                data = json.load(f)
                return data.get("email", None)
        return None

    def clear_last_user():
        if os.path.exists(DEVICE_FILE):
            os.remove(DEVICE_FILE)

# --- Session init ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# --- Sidebar styling ---
st.markdown(
    """
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
    """,
    unsafe_allow_html=True
)

# --- Account System ---
registered_email = get_last_user()

# If cookies library isn't available, show a visible warning so the developer/user can install it.
if not COOKIE_MANAGER_AVAILABLE:
    st.warning(
        "Note: 'streamlit-cookies-manager' is not installed. "
        "The app is using a server-side fallback (device_last_user.json) which will be shared "
        "when the app runs on a central host. For true per-device (browser) persistence, run:\n\n"
        "`pip install streamlit-cookies-manager`"
    )

if registered_email is None:
    st.title("Max-AI Registration System (Per-Device)")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Register / Login"):
        if not username or not password:
            st.error("Please enter both username and password!")
        else:
            email = f"{username}@max.com"
            if email in accounts:
                # existing account -> attempt login
                if accounts[email]["password"] == hash_password(password):
                    save_last_user(email)  # persist login on this device/browser
                    st.success("Login successful!")
                    # re-run to switch into the logged-in UI immediately
                    st.experimental_rerun()
                else:
                    st.error("Wrong password for this username!")
            else:
                # create new account
                accounts[email] = {"password": hash_password(password), "username": username}
                save_accounts()
                save_last_user(email)  # persist for this device/browser
                st.success(f"Account created! Your email: {email}")
                st.experimental_rerun()
else:
    st.sidebar.title("Chats✨")
    if registered_email not in all_chats:
        all_chats[registered_email] = {}
    user_chats = all_chats[registered_email]

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
        if registered_email in accounts:
            del accounts[registered_email]
        if registered_email in all_chats:
            del all_chats[registered_email]
        save_accounts()
        save_chats()
        clear_last_user()
        st.success("Account deleted! You can now create an account with the same username.")
        # reload to show registration screen
        st.experimental_rerun()

    if st.sidebar.button("🚪 Log Out (This Device)"):
        clear_last_user()
        st.success("Logged out from this device.")
        st.experimental_rerun()

    st.html("<h1 style='font-size:60px;'>Max 🧠</h1>")

    # Configure the GenAI key and model (kept as in your original code)
    genai.configure(api_key="AIzaSyALrcQnmp18z2h2ParAb6PXimCpN0HxX8Y")
    text_model = genai.GenerativeModel("gemini-2.0-flash")

    intro_placeholder = st.empty()
    if len(st.session_state.messages) == 0:
        intro_placeholder.markdown(
            f"<div style='display: flex; justify-content: center; align-items: center; height: 65vh; font-size: 3rem; font-weight: bold; color: white; opacity: 0.5;'>Hello, {accounts[registered_email]['username']}!</div>",
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
        if selected_chat_id:
            user_chats[selected_chat_id]["messages"] = st.session_state.messages
            save_chats()

    st.markdown(
        """
        <style>
            .footer {position: fixed; left: 0; bottom: 0; width: 100%; background-color: #1f2937; color: #f9fafb; text-align: center; padding: 0.75rem 0; font-size: 0.875rem; opacity: 0.85; border-top: 1px solid #374151;}
            .footer a {color: #3b82f6; text-decoration: underline;}
        </style>
        <div class="footer">Max can make mistakes. Please verify important information. See <a href="#">Cookie Preferences</a>.</div>
        """,
        unsafe_allow_html=True
            )
