import ollama
import streamlit as st
st.title("welcome to my chatbot app!!")
if "messages" not in st.session_state:
    st.session_state.messages = []
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
question = st.chat_input("ask the question:")
if question:
    st.session_state.messages .append(
        {"role":"user",
         "content": question})
    with st.chat_message("user"):
        st.write(question)
    with st.spinner("Loading..."):
        response = ollama.chat(
            model="llama3.2:3b",
            messages=st.session_state.messages )
        st.session_state.messages .append(
            {"role":"assistant",
            "content":response["message"]["content"]}
        )
    with st.chat_message("assistant"):
            st.write("AI:",response["message"]["content"])
with st.sidebar:
    uploaded_file = st.file_uploader("Upload a text file...")
    if uploaded_file:
        st.write("File uploaded successfully")
        context = uploaded_file.read()
        st.write(context)