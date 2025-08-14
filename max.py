import streamlit as st
import google.generativeai as genai
import os

# --- Config ---
st.set_page_config(page_title="Max-AI by Debayan", page_icon="🧠")

# --- Read credentials from data.txt ---
def load_users(file_path="data.txt"):
    users = {}
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 2:
                    users[parts[0]] = parts[1]
    return users

# --- Login System ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Login to Max-AI")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        users = load_users("data.txt")
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")
    st.stop()

# --- AI Chat UI ---
st.title("Max 🧠")
genai.configure(api_key="AIzaSyALrcQnmp18z2h2ParAb6PXimCpN0HxX8Y")
text_model = genai.GenerativeModel("gemini-2.0-flash")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Placeholder for intro text ---
intro_placeholder = st.empty()

# Show intro only before chat starts
if len(st.session_state.messages) == 0:
    intro_placeholder.markdown(
        f"""
        <div style='
            display: flex;
            justify-content: center;
            align-items: center;
            height: 65vh;
            font-size: 8rem;
            font-weight: bold;
            color: white;
            opacity: 0.5;
        '>
            Max
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Display Chat History ---
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user", avatar="😀").write(msg["content"])
    else:
        st.chat_message("assistant", avatar="😎").write(msg["content"])

# --- Chat Input ---
prompt = st.chat_input("Type here...")

if prompt:
    intro_placeholder.empty()  # Remove intro
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="😀").write(prompt)

    # Prepare conversation history
    history_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages])

    # Generate AI reply
    with st.spinner("Thinking..."):
        try:
            reply = text_model.generate_content(history_text).text
        except Exception as e:
            reply = f"Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant", avatar="😎").write(reply)
