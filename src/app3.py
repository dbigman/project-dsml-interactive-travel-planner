import json
import streamlit as st
import chromadb
import openai
from datetime import datetime

# Load ChromaDB clients
news_client = chromadb.PersistentClient(path="./chromadb")
municipalities_client = chromadb.PersistentClient(path="./chromadb_municipalities")
landmarks_client = chromadb.PersistentClient(path="./chromadb_landmarks")

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

# Read API key from file
api_key_path = "API_Key.txt"
with open(api_key_path, "r") as file:
    OPENAI_API_KEY = file.read().strip()

openai.api_key = OPENAI_API_KEY

# Function to retrieve information from collections
def retrieve_relevant_info(query, collection):
    results = collection.query(query_texts=[query], n_results=3)  # Adjust as needed
    return results

# Function to maintain conversation memory and log chat history
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

    # Extract text from results
    combined_context = "\n".join(
        str(doc) for docs in context if docs and "documents" in docs 
        for doc in docs["documents"][0] if doc is not None
    )

    # Add previous conversation history
    messages = st.session_state.messages.copy()
    messages.append({"role": "user", "content": user_input})
    
    # Include retrieved context as assistant response before user input
    if combined_context:
        messages.append({"role": "assistant", "content": f"Relevant Information:\n{combined_context}"})

    # Call OpenAI API
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        model_reply = response.choices[0].message.content
        
        # Append to conversation history
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": model_reply})

        # Log the conversation
        log_chat(user_input, model_reply)

        return model_reply
    except Exception as e:
        return f"Error: {e}"

# Function to log chat history for analysis
def log_chat(user_input, model_reply):
    chat_data = {
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input,
        "model_reply": model_reply
    }
    with open("chat_logs.jsonl", "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(chat_data) + "\n")

# Streamlit UI for interaction
st.title("Chat with ChatGPT using RAG system")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] != "system":  # Skip displaying system messages
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# User input
user_input = st.chat_input("Ask me anything...")
if user_input:
    # Get the response from the LLM
    model_reply = chat_with_llm(user_input)

    # Display AI response
    with st.chat_message("assistant"):
        st.markdown(model_reply)
