import ollama
import streamlit as st
st.title(":rainbow[chatbot]")
with st.sidebar:
     st.header("chat settings")
     if st.button("clear chat"):
          st.session_state.messages = []
     personalities = {
         "kid":"answer the questions like you are explaining to a 5 year old kid give in 2 lines only",
         "friend":"answer friendly and casual give in 2 lines only"
     }
     personality = st.selectbox("select a personality",personalities.keys())
     uploaded_file = st.file_uploader("upload a text file..")
     try:
         if uploaded_file:
              st.success("success")
              if st.button("Display"):
                  context = uploaded_file.read().decode("utf-8")
                  st.text(context)
     except:
          st.error("error")

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
            messages=[
                {"role":"system","content":personalities[personality
                                                         ]}]
                +st.session_state.messages )
        st.session_state.messages .append(
            {"role":"assistant",
            "content":response["message"]["content"]}
        )
        with st.chat_message("assistant"):
            st.write("AI:",response["message"]["content"])