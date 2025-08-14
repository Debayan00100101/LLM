import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64

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
    st.session_state.messages = []  # role: "user"/"assistant", content: str or {"image":...}

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

# --- Chat Input ---
if prompt := st.chat_input("Type a message or 'image: your prompt'..."):
    # Save and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="😀").write(prompt)

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
                history_text = "\n".join([f"{m['role'].capitalize()}: {m['content'] if isinstance(m['content'], str) else '[Image]'}"
                                          for m in st.session_state.messages])
                reply = text_model.generate_content(history_text).text
            except Exception as e:
                reply = f"Error: {e}"
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant", avatar="😎").write(reply)
