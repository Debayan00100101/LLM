import streamlit as st
import google.generativeai as genai
st.set_page_config(page_title="Max-AI Agent by Debayan",page_icon="🧠")
st.title("Max")
genai.configure(api_key="AIzaSyCFdHMPJiR7hotEWC0tQqTR2cxl1qf6veE")
model = genai.GenerativeModel("gemini-2.0-flash")
query = F'{st.text_input("🔎 Enter your search prompt", placeholder="Type Here...")}'

if query:
    respons = model.generate_content(F"prompt: {query}")
    st.info(F"{respons.text}",icon="🧠")