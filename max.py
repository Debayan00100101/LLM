import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# ---------- Page Config ----------
st.set_page_config(page_title="Max-AI by Debayan", page_icon="🧠")
st.title("Max-AI 🧠")

# ---------- Configure Gemini ----------
genai.configure(api_key="AIzaSyDDwpm0Qt8-L424wY1oXcJThjZwFDeiUNI")
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------- Session State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- Show Chat History ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg.get("avatar", None)):
        st.markdown(msg["content"])

# ---------- File Upload ----------
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

# ---------- Chat Input at Bottom ----------
if prompt := st.chat_input("Type your message here..."):
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "avatar": "😀"
    })

    # Prepare message parts
    parts = [{"text": prompt}]

    # If image uploaded, add it
    if uploaded_file:
        img = Image.open(uploaded_file)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes = img_bytes.getvalue()
        parts.append({
            "inline_data": {
                "mime_type": "image/png",
                "data": img_bytes
            }
        })

    # Generate response
    response = model.generate_content([{"role": "user", "parts": parts}])

    # Add AI response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response.text,
        "avatar": "😎"
    })

    # Show AI message immediately
    with st.chat_message("assistant", avatar="😎"):
        st.markdown(response.text)
