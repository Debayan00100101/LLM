import streamlit as st
import google.generativeai as genai


st.set_page_config(page_title="Max-AI Agent by Debayan", page_icon="🧠")
st.title("Max")

try:
    genai.configure(api_key="AIzaSyDDwpm0Qt8-L424wY1oXcJThjZwFDeiUNI")
    

    model = genai.GenerativeModel("gemini-2.0-flash")

    query = st.text_input("🔎 Enter your search prompt", placeholder="Type Here...")


    if query:
        st.spinner("Thinking...", icon="🧠")

        response = model.generate_content(query)
        st.info(f"{response.text}", icon="🧠")

except Exception as e:

    st.error(f"An error occurred: {e}")

