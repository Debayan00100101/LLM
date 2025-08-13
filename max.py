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
# This dictionary stores the messages to keep the conversation going.
# 'messages' will hold a list of dictionaries with 'role' and 'content'.
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Previous Messages ---
# Loop through the messages in the session state and display them.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Handle New User Input ---
# Create a text input for the user to type their message.
if prompt := st.chat_input("What is up?"):
    # Add the user's message to the chat history.
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display the user's message in the chat.
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- Generate and Display AI Response ---
    with st.chat_message("assistant"):
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
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
            except Exception as e:
                st.error(f"An error occurred while generating the response: {e}")
