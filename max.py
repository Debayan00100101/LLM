import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up the Streamlit page configuration
st.set_page_config(page_title="Max-AI Agent by Debayan", page_icon="🧠")
st.title("Max")

# Configure the Generative AI API with the API key from the environment variable
api_key = os.getenv("AIzaSyCFdHMPJiR7hotEWC0tQqTR2cxl1qf6veE")
if not api_key:
    st.error("API key not found. Please set the GOOGLE_API_KEY environment variable.")
    st.stop()

genai.configure(api_key=api_key)

# Initialize the generative model
model = genai.GenerativeModel("gemini-2.0-flash")

# Get user input
query = st.text_input("🔎 Enter your search prompt", placeholder="Type Here...")

# If the user has entered a query, generate content
if query:
    try:
        # Call the API with the raw user query
        response = model.generate_content(query)
        st.info(f"{response.text}", icon="🧠")
    except Exception as e:
        st.error(f"An error occurred: {e}")
