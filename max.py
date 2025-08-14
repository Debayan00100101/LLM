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

# --- Empty State (Centered "Max") ---
if not st.session_state.messages:
    st.markdown(
        """
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
