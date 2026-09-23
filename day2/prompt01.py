import ollama
response = ollama.chat(
    model="llama3.2:3b",
    messages=[
        {
            "role":"user",
            "content":"Define Ai give types of Ai with examples in three lines"
        }
    ]
)
print(response["message"]["content"])