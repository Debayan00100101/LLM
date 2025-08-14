import streamlit as st
import google.generativeai as genai

# --- Page Config ---
st.set_page_config(page_title="Max-AI Agent by Debayan", page_icon="🧠")
st.title("Max - AI Agent")

# --- Configure Gemini API ---
genai.configure(api_key="AIzaSyDDwpm0Qt8-L424wY1oXcJThjZwFDeiUNI")
model = genai.GenerativeModel("gemini-2.0-flash")

# --- Session State for Memory ---
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": "user"/"assistant", "content": str}

# --- Display Chat History ---
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user", avatar="😀").write(msg["content"])
    else:
        st.chat_message("assistant", avatar="😎").write(msg["content"])

# --- Chat Input ---
if prompt := st.chat_input("Type your message..."):
    # Save and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="😀").write(prompt)

    # Get AI response
    with st.spinner("Thinking..."):
        try:
            history_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages])
            response = model.generate_content(history_text)
            reply = response.text
        except Exception as e:
            reply = f"Error: {e}"

    # Save and display AI reply
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant", avatar="😎").write(reply)
