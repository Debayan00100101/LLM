import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64
import tempfile

# --- Streamlit Page Config ---
st.set_page_config(page_title="Max-AI by Debayan", page_icon="🧠")
st.title("Max 🧠")

# --- Configure Gemini API ---
genai.configure(api_key="AIzaSyDDwpm0Qt8-L424wY1oXcJThjZwFDeiUNI")

# Models
text_model = genai.GenerativeModel("gemini-2.0-flash")
image_model = genai.GenerativeModel("gemini-1.5-flash")  # supports images

# --- Session State for Memory ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello 👋, there how can I assist you today?"}
    ]

# --- Display Chat History ---
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user", avatar="😀").write(msg["content"])
    else:
        with st.chat_message("assistant", avatar="😎"):
            if isinstance(msg["content"], str):
                st.write(msg["content"])
            elif isinstance(msg["content"], dict) and "image" in msg["content"]:
                st.image(msg["content"]["image"], caption="Generated Image")

# --- Sidebar for Inputs ---
st.sidebar.header("Extra Inputs")

# File upload (PDF, TXT, Image, etc.)
uploaded_file = st.sidebar.file_uploader("Upload a file (text, pdf, image)", type=["txt", "pdf", "png", "jpg", "jpeg"])
uploaded_image = None
file_text_content = ""

if uploaded_file:
    if uploaded_file.type.startswith("image"):
        uploaded_image = Image.open(uploaded_file)
        st.sidebar.image(uploaded_image, caption="Uploaded Image")
    else:
        file_text_content = uploaded_file.read().decode(errors="ignore")
        st.sidebar.write("File content loaded.")

# Audio upload (Voice Input)
uploaded_audio = st.sidebar.file_uploader("Upload voice (wav, mp3, m4a)", type=["wav", "mp3", "m4a"])
audio_text = ""

if uploaded_audio:
    st.sidebar.audio(uploaded_audio)
    # No speechrecognition — we'll just treat audio as input and mention it in chat
    audio_text = "[Voice message uploaded]"

# --- Chat Input ---
if prompt := st.chat_input("Type Here..."):
    # Combine file content / audio text with prompt
    combined_input = prompt
    if file_text_content:
        combined_input += "\n\n[File content]:\n" + file_text_content
    if audio_text:
        combined_input += "\n\n" + audio_text
    if uploaded_image:
        combined_input += "\n\n[Image uploaded]"

    # Save and display user message
    st.session_state.messages.append({"role": "user", "content": combined_input})
    st.chat_message("user", avatar="😀").write(combined_input)

    # --- Image Generation Mode ---
    if prompt.lower().startswith("image:"):
        image_prompt = prompt[6:].strip()
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

    # --- Text Generation Mode ---
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
