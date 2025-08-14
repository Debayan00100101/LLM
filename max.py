import streamlit as st
import google.generativeai as genai
from streamlit_oauth import OAuth2Component

# --- Streamlit Page Config ---
st.set_page_config(page_title="Max-AI by Debayan", page_icon="🧠")
st.title("Max 🧠")

# --- Configure Gemini API ---
genai.configure(api_key="AIzaSyALrcQnmp18z2h2ParAb6PXimCpN0HxX8Y")
text_model = genai.GenerativeModel("gemini-2.0-flash")

# --- Google OAuth Login ---
oauth_component = OAuth2Component(
    client_id="YOUR_GOOGLE_CLIENT_ID",
    client_secret="YOUR_GOOGLE_CLIENT_SECRET",
    scopes=["openid", "email", "profile"],
)

user_info = oauth_component.login("Login with Google")

if user_info:
    st.success(f"Logged in as {user_info['email']}")
    
    # Save user info to data.txt
    with open("data.txt", "a") as f:
        f.write(f"{user_info['email']}, {user_info['name']}\n")

    # --- Session State for Chat ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # --- Intro Placeholder ---
    intro_placeholder = st.empty()

    if len(st.session_state.messages) == 0:
        intro_placeholder.markdown(
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

    # --- Display Saved Chat History ---
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user", avatar="😀").write(msg["content"])
        else:
            st.chat_message("assistant", avatar="😎").write(msg["content"])

    # --- Chat Input ---
    prompt = st.chat_input("Type here...")
    if prompt:
        intro_placeholder.empty()
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user", avatar="😀").write(prompt)

        history_text = "\n".join([
            f"{m['role'].capitalize()}: {m['content']}"
            for m in st.session_state.messages
        ])

        with st.spinner("Thinking..."):
            try:
                reply = text_model.generate_content(history_text).text
            except Exception as e:
                reply = f"Error: {e}"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant", avatar="😎").write(reply)

else:
    st.info("Please log in with Google to continue.")
