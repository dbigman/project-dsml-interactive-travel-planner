import chromadb
import openai
from dotenv import load_dotenv
import logging
from icecream import ic
import os
import sys
import streamlit as st
import datetime
import json
from chromadb import Client

# -------------------------
# 1. Logging Setup
# -------------------------
logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.hasHandlers():
    logger.handlers.clear()

file_handler = logging.FileHandler("chatbot_correction.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.info("Logging initialized.")

# -------------------------
# 2. Load Environment Variables & Setup OpenAI
# -------------------------
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logger.error("OpenAI API key is missing! Check your .env file.")
    raise ValueError("OpenAI API key not found.")
logger.info("OpenAI API key loaded successfully.")

openai.api_key = openai_api_key
openai.api_type = "openai"  # Set to "azure" if you are using Azure OpenAI
logger.info("OpenAI configuration set. API type: openai.")

# -------------------------
# 3. Setup a Single ChromaDB Client and Load Collections
# -------------------------
# Create a single persistent client pointing to the main ChromaDB directory.
client = chromadb.PersistentClient(path="../chromadb")
logger.info("ChromaDB client initialized.")

def load_chromadb_collection(client, collection_name):
    logger.info(f"Attempting to load collection: {collection_name}")
    try:
        collection = client.get_collection(collection_name)
        logger.info(f"SUCCESS: loaded collection: {collection_name}")
        return collection
    except Exception as e:
        logger.error(f"ERROR: loading collection {collection_name}: {e}")
        return None

# Load all three collections using the same client
municipalities_collection = load_chromadb_collection(client, "municipalities")
news_collection = load_chromadb_collection(client, "news_articles")
landmarks_collection = load_chromadb_collection(client, "landmarks")

# Debugging statements to verify collections
if municipalities_collection is None:
    logger.error("ERROR: municipalities_collection failed to load.")
else:
    logger.info("SUCCESS: municipalities_collection loaded successfully.")

if news_collection is None:
    logger.error("ERROR: news_collection failed to load.")
else:
    logger.info("SUCCESS: news_collection loaded successfully.")

if landmarks_collection is None:
    logger.error("ERROR: landmarks_collection failed to load.")
else:
    logger.info("SUCCESS: landmarks_collection loaded successfully.")

# Quick test: Retrieve and log documents from the news_articles collection
if news_collection:
    docs = news_collection.get()
    ic(f"Documents in collection 'news_articles':", docs)

# -------------------------
# 4. Retrieve Relevant Information from Collections
# -------------------------
def retrieve_relevant_info(query, collection):
    logger.info(f"Querying collection for query: {query}")
    results = collection.query(query_texts=[query], n_results=3)
    logger.info(f"Query results: {results}")
    return results

# -------------------------
# 5. Chat Function with Retrieval-Augmented Generation (RAG)
# -------------------------
def log_chat(user_input, model_reply):
    chat_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "user_input": user_input,
        "model_reply": model_reply
    }
    try:
        with open("chat_logs.jsonl", "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(chat_data) + "\n")
        logger.info("Chat logged: " + json.dumps(chat_data))
    except Exception as e:
        logger.error("Error writing to chat_logs.jsonl: " + str(e))

def chat_with_llm(user_input):
    logger.info(f"Processing user input: {user_input}")
    context = []
    
    # Retrieve context from each collection
    if municipalities_collection:
        municipalities_info = retrieve_relevant_info(user_input, municipalities_collection)
        ic(municipalities_info)
        context.append(municipalities_info)
    if landmarks_collection:
        landmarks_info = retrieve_relevant_info(user_input, landmarks_collection)
        ic(landmarks_info)
        context.append(landmarks_info)
    if news_collection:
        news_info = retrieve_relevant_info(user_input, news_collection)
        ic(news_info)
        context.append(news_info)
    
    combined_context_parts = []
    for docs in context:
        if docs and "documents" in docs:
            logger.info("docs['documents'] content: " + str(docs["documents"]))
            if isinstance(docs["documents"], list) and docs["documents"]:
                sublist = docs["documents"][0]
                for doc in sublist:
                    if doc:
                        combined_context_parts.append(str(doc))
            else:
                for doc in docs["documents"]:
                    if doc:
                        combined_context_parts.append(str(doc))
    combined_context = "\n".join(combined_context_parts)
    logger.info("Combined context after processing: " + combined_context)
    
    if combined_context.strip() == "":
        prompt = (
            f"{user_input}\n\n"
            "Please answer using your travel planning expertise about Puerto Rico. "
        )
        system_message = "You are a helpful travel planner assistant for Puerto Rico."
        logger.info("No context found, using general travel planning prompt.")
    else:
        prompt = (
            f"{user_input}\n\n"
            f"Context:\n{combined_context}\n\n"
            "Answer using only the provided context."
        )
        system_message = "You are a helpful travel planner assistant. Use only the provided context."
    
    try:
        response = openai.chat.completions.create(
            model="o3-mini-2025-01-31",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            reasoning_effort='low'
        )
        model_reply = response.choices[0].message.content
        logger.info("Received model reply: " + model_reply)
        log_chat(user_input, model_reply)
        ic(model_reply)
        return model_reply
    except Exception as e:
        logger.error(f"Error in chat_with_llm: {e}")
        return f"Error: {e}"

# -------------------------
# 6. Streamlit UI for Chatbot
# -------------------------
st.title("Puerto Rico Travel Planner Chatbot")
logger.info("Streamlit app started.")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Welcome to your Puerto Rico Travel Planner! How can I help you plan your trip today?"
    })
    logger.info("Added introductory message to chat history.")

col1, col2 = st.columns([3, 1])  # Chat on the left, logs on the right

with col1:
    # Display chat history
    for msg in st.session_state.messages:
        logger.info(f"Displaying message - Role: {msg['role']}, Content: {msg['content']}")
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input area
    user_input = st.chat_input("Ask me anything about Puerto Rico...")
    if user_input:
        logger.info("User input received: " + user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        model_reply = chat_with_llm(user_input)
        st.session_state.messages.append({"role": "assistant", "content": model_reply})
        logger.info("Assistant reply appended to session state.")
        with st.chat_message("assistant"):
            st.markdown(model_reply)

with col2:
    st.markdown("### Chat Logs")
    with st.expander("View Chat Logs", expanded=True):
        try:
            if os.path.exists("chat_logs.jsonl"):
                with open("chat_logs.jsonl", "r", encoding="utf-8") as log_file:
                    logs = log_file.read()
                st.text_area("Chat Logs", logs, height=200, max_chars=5000)
                logger.info("Chat logs displayed in dashboard.")
            else:
                st.write("No chat logs found.")
        except Exception as e:
            st.error("Error loading chat logs: " + str(e))
            logger.error("Error loading chat logs: " + str(e))
