from sentence_transformers import SentenceTransformer
import chromadb
import ollama
import streamlit as st

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "msgs" not in st.session_state:
    st.session_state.msgs = []


@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


model = load_model()

st.title("My RagBot")

with st.sidebar:
    st.header(":blue[Chat settings]")

    if st.button("Chat history"):
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.session_state.msgs = []
        st.success("Chat cleared 🗑️")

    personalities = {
        "Kid 👶": "Answer the question like you are explaining to a 5 years old kid. Give the answer in 2 lines only.",
        "Friend 👩‍🦱": "Answer the question in a friendly and casual manner. Give the answer in 2 lines only.",
        "Father 🧓": "Answer the question as a father is talking to the daughter. Give the answer in 2 lines only."
    }

    personality = st.selectbox(
        "Select a personality",
        personalities.keys()
    )

    uploaded_file = st.file_uploader("Upload a file")

    if uploaded_file:
        text = uploaded_file.read().decode("utf-8")

        with st.expander("Preview"):
            st.text(text)

        chunks = []
        chunk_size = 100
        chunk_overlap = 20
        step = chunk_size - chunk_overlap

        for i in range(0, len(text), step):
            chunk = text[i:i + chunk_size]
            chunks.append(chunk)

        embeddings = model.encode(chunks)

        client = chromadb.PersistentClient(path="./chroma_db")

        collection = client.get_or_create_collection(
            name="My_documents"
        )

        ids = []

        for i in range(len(chunks)):
            ids.append(f"{uploaded_file.name}_{i}")

        collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings.tolist()
        )


# Query phase
question = st.chat_input("Ask a question....")

if question:

    if uploaded_file:

        with st.chat_message("user"):
            st.write(question)

        question_embedding = model.encode(question)

        results = collection.query(
            query_embeddings=[question_embedding.tolist()],
            n_results=3
        )

        retrieved_results = results["documents"][0]
        retrieved_ids = results["ids"][0]

        # Create context
        context = "\n".join(retrieved_results)

        # Prompting
        prompt = f"""
        Answer the question using the context provided below.

        Question: {question}

        Context: {context}

        Answer:
        """

        # Connecting to local model
        response = ollama.chat(
            model="llama3.2:3b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        answer = response["message"]["content"]

        with st.chat_message("assistant"):
            st.write(answer)

    else:

        # Store user message
        st.session_state.msgs.append(
            {
                "role": "user",
                "content": question
            }
        )

        # Also store for chat history
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        with st.chat_message("user"):
            st.write(question)

        with st.spinner("Thinking..."):

            response = ollama.chat(
                model="llama3.2:3b",
                messages=[
                    {
                        "role": "system",
                        "content": personalities[personality]
                    }
                ] + st.session_state.msgs
            )

        answer = response["message"]["content"]

        # Store assistant response
        st.session_state.msgs.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        with st.chat_message("assistant"):
            st.write(answer)