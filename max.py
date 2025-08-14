import streamlit as st
import google.generativeai as genai

# --- Streamlit Page Config ---
st.set_page_config(page_title="Max-AI by Debayan", page_icon="🧠")
st.title("Max 🧠")
st.write("I can assist you by reasoning math, code also!!!")

# --- Configure Gemini API ---
genai.configure(api_key="AIzaSyALrcQnmp18z2h2ParAb6PXimCpN0HxX8Y")
text_model = genai.GenerativeModel("gemini-2.0-flash")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Placeholder for intro text ---
intro_placeholder = st.empty()

# --- Show intro if no messages yet ---
if len(st.session_state.messages) == 0:
    intro_placeholder.markdown(
        """
        <div style='
            display: flex;
            justify-content: center;
            align-items: center;
            height: 65vh;
            font-size: 6rem;
            font-weight: bold;
            color: white;
            opacity: 0.5;
        '>
            Hello, World!
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Display saved chat history ---
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user", avatar="😀").write(msg["content"])
    else:
        st.chat_message("assistant", avatar="😎").write(msg["content"])
        # Add footer below AI messages
        st.markdown(
            """
            <div style='
                margin-top: 0.5rem;
                padding: 0.5rem 1rem;
                background-color: #1f2937;
                color: #f9fafb;
                border-radius: 0.5rem;
                font-size: 0.875rem;
                text-align: center;
                opacity: 0.85;
            '>
                Max can make mistakes. Please verify important information. See <a href='#' style='color:#3b82f6; text-decoration:underline;'>Cookie Preferences</a>.
            </div>
            """,
            unsafe_allow_html=True
        )

# --- Chat Input ---
prompt = st.chat_input("Type here...")

if prompt:
    # Remove intro instantly
    intro_placeholder.empty()

    # Save & display user message
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

    # Save & display AI message
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant", avatar="😎").write(reply)

    # Add polished footer below AI reply
    st.markdown(
        """
        <div style='
            margin-top: 0.5rem;
            padding: 0.5rem 1rem;
            background-color: #1f2937;
            color: #f9fafb;
            border-radius: 0.5rem;
            font-size: 0.875rem;
            text-align: center;
            opacity: 0.85;
        '>
            Max can make mistakes. Please verify important information. See <a href='#' style='color:#3b82f6; text-decoration:underline;'>Cookie Preferences</a>.
        </div>
        """,
        unsafe_allow_html=True
    )
