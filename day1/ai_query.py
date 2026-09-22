import ollama
response = ollama.chat(
    model="llama3.2:3b",
    messages=[
        {
            "role":"user",
            "content":"explain machine learning in 40 words"
        }
    ]
)
print(response["messages"]["content"])