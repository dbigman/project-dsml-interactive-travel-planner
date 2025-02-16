import chromadb
import openai
from dotenv import load_dotenv
import logging
from icecream import ic
import os
import sys
import streamlit as st

# Print current working directory for debugging
print("Current working directory:", os.getcwd())

# Create a custom logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Clear existing handlers (useful in a notebook if logging was already configured)
if logger.hasHandlers():
    logger.handlers.clear()

# Create handlers: one for file and one for console output
file_handler = logging.FileHandler("landmarks_correction.log")
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Create a formatter and add it to the handlers
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key
openai.api_type = "openai"
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logging.error("OpenAI API key is missing! Check your .env file.")
    raise ValueError("OpenAI API key not found.")

# Since this file is in the src folder, adjust paths to point to the project root
news_client = chromadb.PersistentClient(path="../chromadb")
municipalities_client = chromadb.PersistentClient(path="../chromadb/chromadb_municipalities")
landmarks_client = chromadb.PersistentClient(path="../chromadb/chromadb_landmarks")

# Function to load collections
def load_chromadb_collection(client, collection_name):
    try:
        collection = client.get_collection(collection_name)
        print(f"Successfully loaded collection: {collection_name}")
        return collection
    except Exception as e:
        print(f"Error loading collection {collection_name}: {e}")
        return None

# Load collections
news_collection = load_chromadb_collection(news_client, "news_articles")
municipalities_collection = load_chromadb_collection(municipalities_client, "municipalities")
landmarks_collection = load_chromadb_collection(landmarks_client, "landmarks")

# Set OpenAI API Key
openai.api_key = openai_api_key

# Function to perform retrieval from the collections (RAG)
def retrieve_relevant_info(query, collection):
    # Query the collection with the user's question to get relevant documents
    results = collection.query(query_texts=[query], n_results=3)  # Adjust n_results as needed
    return results

def chat_with_llm(user_input):
    context = []

    # Retrieve relevant info from each collection
    if municipalities_collection:
        municipalities_info = retrieve_relevant_info(user_input, municipalities_collection)
        context.append(municipalities_info)
    
    if landmarks_collection:
        landmarks_info = retrieve_relevant_info(user_input, landmarks_collection)
        context.append(landmarks_info)
    
    if news_collection:
        news_info = retrieve_relevant_info(user_input, news_collection)
        context.append(news_info)

    # Extract text from results while filtering out None values
    combined_context = "\n".join(
        str(doc) for docs in context if docs and "documents" in docs 
        for doc in docs["documents"][0] if doc is not None
    )

    # Build a new prompt that enforces the constraint:
    prompt = (
        f"{user_input}\n\n"
        f"Context:\n{combined_context}\n\n"
        "Answer the above query **using only the provided context**. "
        "If the necessary information is not present in the context, respond with: "
        "'I do not have enough information to answer this question.'"
    )

    try:
        response = openai.chat.completions.create(
            model="o3-mini-2025-01-31",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a helpful assistant. "
                        "Answer the user's query using only the information provided in the context. "
                        "Do not incorporate any external knowledge."
                    )
                },
                {"role": "user", "content": prompt}
            ]
        )
        model_reply = response.choices[0].message.content
        return model_reply
    except Exception as e:
        return f"Error: {e}"



st.title("Chat with ChatGPT using RAG system")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant, always happy to help."}]

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] != "system":  # Skip displaying system message
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# User input
user_input = st.chat_input("Ask me anything...")
if user_input:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Get the response from the LLM
    model_reply = chat_with_llm(user_input)

    # Append AI response
    st.session_state.messages.append({"role": "assistant", "content": model_reply})

    # Display AI response
    with st.chat_message("assistant"):
        st.markdown(model_reply)
