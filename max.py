import streamlit as st
import google.generativeai as genai

# Set up the Streamlit page configuration
st.set_page_config(page_title="Max-AI Agent by Debayan", page_icon="🧠")
st.title("Max")

# Configure the Generative AI API with your hardcoded API key
# WARNING: This is NOT a secure practice.
# Replace "YOUR_API_KEY_HERE" with your actual key.
try:
    genai.configure(api_key="AIzaSyDDwpm0Qt8-L424wY1oXcJThjZwFDeiUNI")
    
    # Initialize the generative model
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    # Get user input
    query = st.text_input("🔎 Enter your search prompt", placeholder="Type Here...")

    # If the user has entered a query, generate content
    if query:
        st.info("Thinking...", icon="🧠")
        # Call the API with the user's raw query, without any prefixes
        response = model.generate_content(query)
        st.info(f"{response.text}", icon="✅")

except Exception as e:
    # Catch any errors from the API call itself, including a bad key
    st.error(f"An error occurred: {e}")

