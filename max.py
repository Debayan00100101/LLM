import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64
import speech_recognition as sr

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

# --- File/Image Input ---
uploaded_file = st.file_uploader("Upload a file or image", type=["png", "jpg", "jpeg", "txt", "pdf"])
if uploaded_file is not None:
    if uploaded_file.type.startswith("image/"):
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Image")
        st.session_state.messages.append({"role": "user", "content": "[Uploaded an image]"})
        with st.spinner("Thinking about the image..."):
            try:
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="PNG")
                img_bytes.seek(0)
                img_base64 = base64.b64encode(img_bytes.read()).decode("utf-8")

                img_response = image_model.generate_content(
                    ["Describe this image:", {"mime_type": "image/png", "data": img_base64}],
                    generation_config={"response_mime_type": "text/plain"}
                )
                reply = img_response.text
            except Exception as e:
                reply = f"Image error: {e}"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant", avatar="😎").write(reply)

    else:
        # Non-image file handling
        file_text = uploaded_file.read().decode(errors="ignore")
        st.session_state.messages.append({"role": "user", "content": f"[Uploaded file: {uploaded_file.name}]"})
        with st.spinner("Reading file..."):
            try:
                reply = text_model.generate_content(f"Here is the file content:\n{file_text}").text
            except Exception as e:
                reply = f"File error: {e}"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant", avatar="😎").write(reply)

# --- Voice Input ---
if st.button("Record Voice"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎤 Listening...")
        audio = recognizer.listen(source)
    try:
        prompt = recognizer.recognize_google(audio)
        st.write(f"You said: {prompt}")
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Thinking..."):
            reply = text_model.generate_content(prompt).text
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant", avatar="😎").write(reply)
    except Exception as e:
        st.write(f"Voice error: {e}")

# --- Text Chat Input ---
if prompt := st.chat_input("Type Here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="😀").write(prompt)

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
