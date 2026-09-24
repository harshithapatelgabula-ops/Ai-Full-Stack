import streamlit as  st
st.title("My first streamlit app!!!")
st.write("Welcome to my AI application!")
name = st.text_input("enter your name:")
if st.button("Submit"):
    st.write("Hello",name)