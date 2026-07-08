from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.1",
    base_url="http://localhost:11434"
)

# Interact the llm like normal by looping, type exit to go back
while(True):
    user_input = str(input())

    if user_input == "exit":
        break

    response = llm.invoke(user_input)
    print(response.content)