import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import tempfile
import os
import wave

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
if "voice_text" not in st.session_state:
    st.session_state.voice_text = None
if "uploaded_file_data" not in st.session_state:
    st.session_state.uploaded_file_data = None

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

# --- Browser Voice Input ---
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = []
    def recv_audio(self, frame):
        self.frames.append(frame.to_ndarray().tobytes())
        return frame

# Input area with tabs for different input methods
tab_text, tab_file, tab_voice = st.tabs(["Type...", "File/Image", "🎤Voice"])

with tab_text:
    prompt = st.chat_input("Type your message here...")

with tab_file:
    uploaded_file = st.file_uploader("Upload a file or image", type=None)
    if uploaded_file:
        st.session_state.uploaded_file_data = uploaded_file
        prompt = f"[Uploaded {uploaded_file.name}]"

with tab_voice:
    webrtc_ctx = webrtc_streamer(
        key="speech",
        mode=WebRtcMode.SENDONLY,
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
    )
    if webrtc_ctx.audio_processor and st.button("Stop Recording & Process"):
        temp_audio_path = tempfile.mktemp(suffix=".wav")
        wf = wave.open(temp_audio_path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        wf.writeframes(b''.join(webrtc_ctx.audio_processor.frames))
        wf.close()
        with open(temp_audio_path, "rb") as f:
            audio_data = f.read()
        try:
            transcribe_model = genai.GenerativeModel("gemini-1.5-flash")
            result = transcribe_model.generate_content(
                [genai.types.Part.from_bytes(audio_data, mime_type="audio/wav")]
            )
            st.session_state.voice_text = result.text
            st.success(f"Voice input: {result.text}")
            prompt = result.text
        except Exception as e:
            st.error(f"Transcription error: {e}")
        os.remove(temp_audio_path)

# Handle file uploads
if st.session_state.uploaded_file_data:
    file = st.session_state.uploaded_file_data
    try:
        if file.type.startswith("image/"):
            img = Image.open(file)
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
            content = file.read().decode(errors="ignore")
            st.session_state.messages.append({"role": "user", "content": f"[Uploaded File]\n{content}"})
            st.chat_message("user", avatar="😀").write(content)
    except Exception as e:
        st.error(f"File error: {e}")
    st.session_state.uploaded_file_data = None

# Process voice text
if st.session_state.voice_text and not prompt:
    prompt = st.session_state.voice_text
    st.session_state.voice_text = None

# --- Chat Handling ---
if prompt:
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
