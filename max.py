import streamlit as st
import google.generativeai as genai
from PIL import Image
import io, base64, tempfile
from PyPDF2 import PdfReader
import docx
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
import speech_recognition as sr  # OPTIONAL, will work only locally with mic
import os

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Max-AI", page_icon="🧠")
st.title("Max-AI")

API_KEY = "AIzaSyDDwpm0Qt8-L424wY1oXcJThjZwFDeiUNI"  # Your Gemini API key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

# ======================
# FUNCTIONS
# ======================
def read_file_content(uploaded_file):
    """Extract text from TXT, PDF, DOCX files."""
    if uploaded_file.type == "text/plain":
        return uploaded_file.read().decode("utf-8")
    elif uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        return "\n".join(page.extract_text() for page in reader.pages)
    elif uploaded_file.type in [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword"
    ]:
        doc = docx.Document(uploaded_file)
        return "\n".join([p.text for p in doc.paragraphs])
    else:
        return None

def encode_image(uploaded_image):
    """Convert image to base64 for Gemini."""
    image = Image.open(uploaded_image)
    buffered = io.BytesIO()
    image_format = "PNG" if uploaded_image.type == "image/png" else "JPEG"
    image.save(buffered, format=image_format)
    img_bytes = buffered.getvalue()
    return {
        "mime_type": uploaded_image.type,
        "data": base64.b64encode(img_bytes).decode()
    }

# ======================
# SIDEBAR
# ======================
with st.sidebar:
    st.header("Upload")
    uploaded_file = st.file_uploader("Upload a file", type=["txt", "pdf", "docx"])
    uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

# ======================
# TEXT CHAT
# ======================
prompt = st.text_input("Enter your message:")

# ======================
# VOICE CHAT
# ======================
st.subheader("Voice Input (optional)")
def process_audio(frame):
    audio = frame.to_ndarray()
    return av.AudioFrame.from_ndarray(audio, layout="mono")

webrtc_streamer(key="voice", mode=WebRtcMode.SENDONLY, audio_receiver_size=256)

# ======================
# SEND PROMPT
# ======================
if st.button("Send"):
    contents = []

    # If image uploaded
    if uploaded_image:
        contents.append(encode_image(uploaded_image))

    # If file uploaded
    if uploaded_file:
        file_text = read_file_content(uploaded_file)
        if file_text:
            contents.append(file_text)

    # Always add text prompt
    if prompt.strip():
        contents.append(prompt)

    if contents:
        response = model.generate_content(contents)
        st.write("**Assistant:**", response.text)
    else:
        st.warning("Please enter text, upload a file, or upload an image.")

