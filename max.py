import streamlit as st
import google.generativeai as genai

# Set up the Streamlit page configuration
st.set_page_config(page_title="Max-AI Agent by Debayan", page_icon="🧠")
st.title("Max-AI Chat")

# --- API Key Configuration ---
# WARNING: Hardcoding your API key is not secure.
try:
    genai.configure(api_key="AIzaSyDDwpm0Qt8-L424wY1oXcJThjZwFDeiUNI")
    
    # Initialize the generative model
    model = genai.GenerativeModel("gemini-2.0-flash")

except Exception as e:
    st.error(f"An error occurred during API key configuration: {e}")
    st.stop()

# --- Initialize Chat History in Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Previous Messages with Emojis ---
for message in st.session_state.messages:
    # Use the default chat message, but then add the emoji inside
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(f"😀 **You**\n\n{message['content']}")
        else:
            st.markdown(f"😎 **AI**\n\n{message['content']}")

# --- Handle New User Input ---
if prompt := st.chat_input("What is up?"):
    # Add the user's message to the chat history.
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display the user's message in the chat with the emoji.
    # The avatar parameter is removed, so Streamlit will use the default user icon.
    with st.chat_message("user"):
        st.markdown(f"😀 **You**\n\n{prompt}")

    # --- Generate and Display AI Response ---
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # The model receives the full chat history to remember context.
                response = model.generate_content(st.session_state.messages, stream=True)
                
                ai_response = ""
                full_response_placeholder = st.empty()
                
                # Stream the response chunk by chunk
                for chunk in response:
                    if chunk.text:
                        ai_response += chunk.text
                        full_response_placeholder.markdown(f"😎 **AI**\n\n{ai_response}")
                        
                # Add the final, full AI response to the chat history.
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
            except Exception as e:
                st.error(f"An error occurred while generating the response: {e}")
