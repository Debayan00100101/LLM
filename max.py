import streamlit as st
import google.generativeai as genai
from PIL import Image
import base64
import io

# -------------------
# Streamlit Config
# -------------------
st.set_page_config(page_title="Max-AI Agent by Debayan", page_icon="🧠")
st.title("Max - AI Agent (Text + Image)")

# -------------------
# Gemini API Config
# -------------------
genai.configure(api_key="AIzaSyDDwpm0Qt8-L424wY1oXcJThjZwFDeiUNI")  # <-- replace or use st.secrets["GEMINI_API_KEY"]

# Models
text_model = genai.GenerativeModel("gemini-2.0-flash")
image_model = genai.GenerativeModel("gemini-1.5-flash")  # can generate images

# -------------------
# Session State for Chat Memory
# -------------------
if "messages" not in st.session_state:
    st.session_state.messages = []  # [{"role": "user"/"assistant", "content": str or {"image": Image}}]

# -------------------
# Function to Generate Image
# -------------------
def generate_image(prompt: str) -> Image.Image:
    result = image_model.generate_content(
        prompt,
        generation_config={"response_mime_type": "image/png"}
    )
    image_base64 = result.candidates[0].content.parts[0].inline_data.data
    image_bytes = base64.b64decode(image_base64)
    return Image.open(io.BytesIO(image_bytes))

# -------------------
# Display Chat History
# -------------------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user", avatar="😀").write(msg["content"])
    else:
        with st.chat_message("assistant", avatar="😎"):
            if isinstance(msg["content"], str):
                st.write(msg["content"])
            elif isinstance(msg["content"], dict) and "image" in msg["content"]:
                st.image(msg["content"]["image"], caption="Generated Image")

# -------------------
# Chat Input
# -------------------
if prompt := st.chat_input("Type text or 'image: your prompt'..."):
    # Save & display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="😀").write(prompt)

    # -------------------
    # Image Request
    # -------------------
    if prompt.lower().startswith("image:"):
        image_prompt = prompt[6:].strip()
        with st.spinner("Generating image..."):
            try:
                img = generate_image(image_prompt)
                st.session_state.messages.append({"role": "assistant", "content": {"image": img}})
                st.chat_message("assistant", avatar="😎").image(img, caption="Generated Image")
            except Exception as e:
                error_msg = f"Image error: {e}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                st.chat_message("assistant", avatar="😎").write(error_msg)

    # -------------------
    # Text Request
    # -------------------
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
