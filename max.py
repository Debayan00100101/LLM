import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64

# --- Streamlit Page Config ---
st.set_page_config(page_title="Max-AI by Debayan", page_icon="🧠")
st.title("Max 🧠")

# --- Configure Gemini API ---
genai.configure(api_key="YOUR_API_KEY")

# Models
text_model = genai.GenerativeModel("gemini-2.0-flash")
image_model = genai.GenerativeModel("gemini-1.5-flash")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello 👋, how can I assist you today?"}
    ]

# --- Chat History Display ---
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user", avatar="😀").write(msg["content"])
    else:
        with st.chat_message("assistant", avatar="😎"):
            if isinstance(msg["content"], str):
                st.write(msg["content"])
            elif isinstance(msg["content"], dict) and "image" in msg["content"]:
                st.image(msg["content"]["image"], caption="Generated Image")

# --- Custom Input Bar ---
st.markdown("""
    <style>
    .input-bar {
        display: flex;
        gap: 8px;
        align-items: center;
        background: #f0f2f6;
        padding: 8px;
        border-radius: 12px;
    }
    .input-text {
        flex: 1;
    }
    .stFileUploader {
        margin-top: -5px;
    }
    </style>
""", unsafe_allow_html=True)

with st.container():
    col1, col2 = st.columns([8, 2])
    with col1:
        user_input = st.text_input("Type here...", label_visibility="collapsed", key="chat_input")
    with col2:
        file_upload = st.file_uploader("", type=["png", "jpg", "jpeg", "pdf", "txt"], label_visibility="collapsed", key="file_upload")

# --- File Logic ---
if file_upload:
    try:
        if file_upload.type.startswith("image/"):
            img = Image.open(file_upload)
            st.session_state.messages.append({"role": "user", "content": "[Uploaded Image]"})
            st.chat_message("user", avatar="😀").image(img, caption="Uploaded Image")
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            with st.spinner("Analyzing image..."):
                try:
                    img_response = image_model.generate_content(
                        [genai.types.Part.from_bytes(img_bytes.read(), mime_type="image/png")]
                    )
                    reply = img_response.text
                except Exception as e:
                    reply = f"Image processing error: {e}"
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.chat_message("assistant", avatar="😎").write(reply)
        else:
            content = file_upload.read().decode(errors="ignore")
            st.session_state.messages.append({"role": "user", "content": f"[Uploaded File]\n{content}"})
            st.chat_message("user", avatar="😀").write(content)
    except Exception as e:
        st.error(f"File error: {e}")

# --- Handle Prompt ---
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user", avatar="😀").write(user_input)

    # Image generation mode
    if user_input.lower().startswith("image:"):
        image_prompt = user_input[6:].strip()
        with st.spinner("Thinking..."):
            try:
                img_response = image_model.generate_content(
                    image_prompt,
                    generation_config={"response_mime_type": "image/png"}
                )
                image_data = img_response.candidates[0].content.parts[0].inline_data.data
                image_bytes = base64.b64decode(image_data)
                img = Image.open(io.BytesIO(image_bytes))
                st.session_state.messages.append({"role": "assistant", "content": {"image": img}})
                st.chat_message("assistant", avatar="😎").image(img, caption="Generated Image")
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"Image error: {e}"})
                st.chat_message("assistant", avatar="😎").write(f"Image error: {e}")

    # Text generation mode
    else:
        with st.spinner("Thinking..."):
            try:
                history_text = "\n".join([
                    f"{m['role'].capitalize()}: {m['content'] if isinstance(m['content'], str) else '[Image]'}"
                    for m in st.session_state.messages
                ])
                reply = text_model.generate_content(history_text).text
            except Exception as e:
                reply = f"Error: {e}"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant", avatar="😎").write(reply)
