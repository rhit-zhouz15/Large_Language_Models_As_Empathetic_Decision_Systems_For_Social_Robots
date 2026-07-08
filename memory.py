from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import datetime

# Create embeddings from llama
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Initialize Chromadb to store turn summaries as embeddings
db = Chroma(
            collection_name="memory",
            embedding_function=embeddings
            # uncomment the bottom line to keep memory throughout sessions instead of only in the current session
            # persist_directory="./memory_db"
        )

def store_memory(page_content: str, turn: int, detected_emotion: str, valence: str, arousal: str):
        memory = Document(
            page_content=page_content,
            metadata={
                "user_id": "kelvin",
                "timestamp": datetime.datetime.now().strftime("%c"),
                "turn": turn,
                "detected emotion": detected_emotion,
                "valence": valence,
                "arousal": arousal
            }
        )

        db.add_documents([memory])

def retrieve_memory(user_input: str, user_id: str):
    contexts = db.similarity_search(
         user_input,
         k=10,
         filter={"user_id": user_id}
    )

    return format_context(contexts)
    
def format_context(contexts: list[Document]):
    formatted = ""
    for doc in contexts:
         content = doc.page_content
         timestamp = doc.metadata.get("timestamp")
         formatted += f"\n{timestamp}: {content}"
    return formatted