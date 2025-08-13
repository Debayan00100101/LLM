import streamlit as st
import google.generativeai as genai

# Set up the Streamlit page configuration
st.set_page_config(page_title="Max-AI Agent by Debayan", page_icon="🧠")
st.title("Max-AI Chat")

# --- API Key Configuration ---
# WARNING: Hardcoding your API key is not secure. Use st.secrets or environment variables in a real-world app.
try:
    genai.configure(api_key="AIzaSyDDwpm0Qt8-L424wY1oXcJThjZwFDeiUNI")
    
    # Initialize the generative model
    model = genai.GenerativeModel("gemini-2.0-flash")

except Exception as e:
    st.error(f"An error occurred during API key configuration: {e}")
    st.stop()

# --- Initialize Chat History in Session State ---
# This list will store messages in the format expected by the Gemini API.
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Previous Messages ---
# Loop through the messages in the session state and display them.
for message in st.session_state.messages:
    # Use avatar=None to remove the avatar icon
    with st.chat_message(message["role"], avatar=None):
        st.markdown(message["parts"][0]["text"])

# --- Handle New User Input ---
# Create a text input for the user to type their message.
if prompt := st.chat_input("What is up?"):
    # Append the user's message in the API's required format.
    st.session_state.messages.append({"role": "user", "parts": [{"text": prompt}]})
    
    # Display the user's message in the chat.
    with st.chat_message("user", avatar=None):
        st.markdown(prompt)

    # --- Generate and Display AI Response ---
    with st.chat_message("assistant", avatar=None):
        with st.spinner("Thinking..."):
            try:
                # The model now receives the full chat history to remember context.
                # `stream=True` makes the response appear word by word.
                response = model.generate_content(st.session_state.messages, stream=True)
                
                # Create a placeholder to stream the response into.
                full_response = st.empty()
                
                # Read the response chunks and append them to the placeholder.
                # This creates the "typewriter" effect.
                ai_response = ""
                for chunk in response:
                    if chunk.text:
                        ai_response += chunk.text
                        full_response.markdown(ai_response)
                        
                # Add the final, full AI response to the chat history.
                st.session_state.messages.append({"role": "assistant", "parts": [{"text": ai_response}]})
                
            except Exception as e:
                st.error(f"An error occurred while generating the response: {e}")
