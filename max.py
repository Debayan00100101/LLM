import streamlit as st
import google.generativeai as genai

# Set up the Streamlit page configuration
st.set_page_config(page_title="Max-AI Agent by Debayan", page_icon="🧠")
st.title("Max")

# Configure the Generative AI API with a securely stored API key
# The API key should be stored in Streamlit's secrets.toml file
# st.secrets["GOOGLE_API_KEY"] refers to the key in that file
try:
    genai.configure(api_key=st.secrets["AIzaSyCFdHMPJiR7hotEWC0tQqTR2cxl1qf6veE"])
except KeyError:
    st.error("API key not found. Please set your Google API key in Streamlit's secrets.")
    st.stop()

# Initialize the generative model
model = genai.GenerativeModel("gemini-2.0-flash")

# Get user input
query = st.text_input("🔎 Enter your search prompt", placeholder="Type Here...")

# If the user has entered a query, generate content
if query:
    try:
        # Call the API with the user's raw query
        response = model.generate_content(query)
        st.info(f"{response.text}", icon="🧠")
    except Exception as e:
        st.error(f"An error occurred: {e}")
