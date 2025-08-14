import streamlit as st
import google.generativeai as genai
from PIL import Image
import tempfile
import os
import io
import base64
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import speech_recognition as sr

# --- Streamlit Page Config ---
st.set_page_config(page_title="Max AI by Debayan", page_icon="🧠")
st.title("Max 🧠")

# --- Gemini API Key (Unsafe Hardcode as requested) ---
API_KEY = "AIzaSyDDwpm0Qt8-L424wY1oXcJThjZwFDeiUNI"
genai.configure(api_key=API_KEY)

# --- Session State for Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Gemini Chat Function ---
def chat_with_gemini(prompt, image_file=None, doc_file=None):
    model = genai.GenerativeModel("gemini-1.5-flash")
    content = [{"role": "user", "parts": [{"text": prompt}]}]

    # Add image if present
    if image_file:
        img = Image.open(image_file)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        content[0]["parts"].append({"mime_type": "image/png", "data": img_bytes.getvalue()})

    # Add document if present
    if doc_file:
        doc_bytes = doc_file.read()
        content[0]["parts"].append({"mime_type": "application/octet-stream", "data": doc_bytes})

    response = model.generate_content(content)
    return response.text

# --- Voice Recording ---
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def recv_audio(self, frame):
        audio_data = frame.to_ndarray().tobytes()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name
        with sr.AudioFile(tmp_path) as source:
            audio = self.recognizer.record(source)
        try:
            text = self.recognizer.recognize_google(audio)
            st.session_state.voice_text = text
        except sr.UnknownValueError:
            st.session_state.voice_text = ""
        os.remove(tmp_path)
        return frame

st.subheader("Chat Input")

# --- Voice Input ---
if st.button("🎤 Record Voice"):
    webrtc_streamer(
        key="voice",
        mode=WebRtcMode.SENDONLY,
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
    )

voice_text = st.session_state.get("voice_text", "")

# --- Text Input ---
user_text = st.text_area("Type your message", value=voice_text, height=100)

# --- File Uploads ---
uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
uploaded_doc = st.file_uploader("Upload File", type=["pdf", "txt", "docx"])

# --- Send Button ---
if st.button("Send"):
    if user_text.strip() == "" and not uploaded_image and not uploaded_doc:
        st.warning("Please enter text, upload an image, or record voice.")
    else:
        response = chat_with_gemini(user_text, uploaded_image, uploaded_doc)
        st.session_state.messages.append(("User", user_text))
        st.session_state.messages.append(("AI", response))

# --- Display Chat History ---
st.subheader("Chat History")
for sender, msg in st.session_state.messages:
    if sender == "User":
        st.markdown(f"**You:** {msg}")
    else:
        st.markdown(f"**AI:** {msg}")
