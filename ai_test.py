import ollama

response = ollama.chat(
    model="llama3.2",
    messages=[
        {
            "role": "user",
            "content": "Give me one simple tip for managing expenses."
        }
    ]
)

print(response["message"]["content"])