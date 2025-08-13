import streamlit as st
import google.generativeai as genai

# Set up the Streamlit page configuration
st.set_page_config(page_title="Max-AI Agent by Debayan", page_icon="🧠")
st.title("Max-AI Chat")

# --- API Key Configuration ---
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

# --- Display Previous Messages ---
for message in st.session_state.messages:
    # Check if the message is a dictionary with a 'parts' key
    if isinstance(message, dict) and "parts" in message and isinstance(message["parts"], list) and len(message["parts"]) > 0:
        with st.chat_message(message["role"]):
            st.markdown(message["parts"][0]["text"])
    else:
        # Handle cases where the message isn't in the expected format
        st.error("Error: Malformed chat history.")

# --- Handle New User Input ---
if prompt := st.chat_input("What is up?"):
    # Append the user's message in the API's required format.
    st.session_state.messages.append({"role": "user", "parts": [{"text": prompt}]})
    
    # Display the user's message in the chat.
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- Generate and Display AI Response ---
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # The model now receives the full chat history in the correct format.
                response = model.generate_content(st.session_state.messages, stream=True)
                
                ai_response = ""
                full_response_placeholder = st.empty()
                
                # Stream the response chunk by chunk
                for chunk in response:
                    if chunk.text:
                        ai_response += chunk.text
                        full_response_placeholder.markdown(ai_response)
                        
                # After the response is complete, save it to the session state
                # in the required API format.
                st.session_state.messages.append({"role": "assistant", "parts": [{"text": ai_response}]})
                
            except Exception as e:
                st.error(f"An error occurred while generating the response: {e}")
