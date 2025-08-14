import streamlit as st
import google.generativeai as genai

# --- Streamlit Page Config ---
st.set_page_config(page_title="Max-AI by Debayan", page_icon="🧠")
st.title("Max 🧠")

# --- Configure Gemini API ---
genai.configure(api_key="AIzaSyDDwpm0Qt8-L424wY1oXcJThjZwFDeiUNI")
text_model = genai.GenerativeModel("gemini-2.0-flash")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.show_intro = True  # Flag to show "Max" intro

# --- Show Intro Message Before Chat Starts ---
if st.session_state.show_intro:
    st.chat_message("assistant", avatar="😎").write("Hello Debayan 👋, I’m Max. How can I help you today?")

# --- Display Chat History ---
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user", avatar="😀").write(msg["content"])
    else:
        st.chat_message("assistant", avatar="😎").write(msg["content"])

# --- Chat Input ---
prompt = st.chat_input("Type here...")

if prompt:
    # Hide intro after first message
    st.session_state.show_intro = False

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="😀").write(prompt)

    # Prepare conversation history for AI
    history_text = "\n".join([
        f"{m['role'].capitalize()}: {m['content']}"
        for m in st.session_state.messages
    ])

    # Generate AI reply
    with st.spinner("Thinking..."):
        try:
            reply = text_model.generate_content(history_text).text
        except Exception as e:
            reply = f"Error: {e}"

    # Add AI message
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant", avatar="😎").write(reply)
