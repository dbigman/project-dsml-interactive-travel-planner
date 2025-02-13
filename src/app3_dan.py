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

# file_handler = logging.FileHandler("chatbot_correction.log")
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
# 3. Setup ChromaDB Clients (Paths adjusted for file in src folder)
# -------------------------
news_client = chromadb.PersistentClient(path="../chromadb")
municipalities_client = chromadb.PersistentClient(path="../chromadb/chromadb_municipalities")
landmarks_client = chromadb.PersistentClient(path="../chromadb/chromadb_landmarks")
logger.info("ChromaDB clients initialized.")

def load_chromadb_collection(client, collection_name):
    """Load a collection from the ChromaDB client.

    This function attempts to retrieve a specified collection from the
    ChromaDB client. It logs the attempt and the result of the operation. If
    the collection is successfully loaded, it is returned; otherwise, an
    error is logged, and None is returned.

    Args:
        client (ChromaDBClient): The ChromaDB client instance used to
            interact with the database.
        collection_name (str): The name of the collection to be loaded.

    Returns:
        Collection or None: The loaded collection if successful,
            otherwise None.
    """

    logger.info(f"Attempting to load collection: {collection_name}")
    try:
        collection = client.get_collection(collection_name)
        logger.info(f"SUCCESS: loaded collection: {collection_name}")
        return collection
    except Exception as e:
        logger.error(f"ERROR: loading collection {collection_name}: {e}")
        return None


# Este esta funcionando
municipalities_collection = load_chromadb_collection(municipalities_client, "municipalities")

# BUG REPORT: The following line is causing an error. 
# The collection is not being loaded.
news_collection = load_chromadb_collection(news_client, "news_articles")
landmarks_collection = load_chromadb_collection(landmarks_client, "landmarks")

# Debugging Statements
if news_collection is None:
    logger.error("ERROR: news_collection failed to load.")
else:
    logger.info("SUCCESS: news_collection loaded successfully.")

if municipalities_collection is None:
    logger.error("ERROR: municipalities_collection failed to load.")
else:
    logger.info("SUCCESS: municipalities_collection loaded successfully.")
    
if landmarks_collection is None:
    logger.error("ERROR: landmarks_collection failed to load.")
else:
    logger.info("SUCCESS: landmarks_collection loaded successfully.")


# inspecting news_collection
# Initialize ChromaDB client
client = Client()

collection = client.get_collection("news_articles")
docs = collection.get()
ic(f"Documents in collection 'your_collection_name':", docs)





# -------------------------
# 4. Retrieve Relevant Information from Collections
# -------------------------
def retrieve_relevant_info(query, collection):
    """Retrieve relevant information from a collection based on a query.

    This function takes a query string and a collection object, then
    retrieves relevant results by querying the collection. It logs the query
    and the results obtained. The function is designed to return a limited
    number of results, specifically the top three matches based on the
    query.

    Args:
        query (str): The query string used to search the collection.
        collection (Collection): The collection object from which to retrieve results.

    Returns:
        list: A list of the top three results that match the query.
    """

    logger.info(f"Querying collection for query: {query}")
    results = collection.query(query_texts=[query], n_results=3)
    logger.info(f"Query results: {results}")
    return results

# -------------------------
# 5. Chat Function with Retrieval-Augmented Generation (RAG)
# -------------------------
# Function to log chat history for analysis
def log_chat(user_input, model_reply):
    """Log chat history for analysis.

    This function records the user input and the model's reply along with a
    timestamp into a JSON Lines file. It appends the chat data to the file
    "chat_logs.jsonl" for future analysis. If an error occurs during the
    file writing process, it logs the error message.

    Args:
        user_input (str): The input provided by the user.
        model_reply (str): The response generated by the model.
    """

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
    """Interact with a language model to generate a response based on user
    input.

    This function processes the user input by retrieving relevant
    information from various collections (municipalities, landmarks, and
    news) and combines this context to formulate a prompt for the language
    model. If no relevant context is found, it defaults to a general travel
    planning prompt. The function then sends this prompt to the OpenAI chat
    model and returns the generated response.

    Args:
        user_input (str): The input provided by the user for which a response
            is to be generated.

    Returns:
        str: The response generated by the language model based on the user
            input and the retrieved context.
    """

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
    user_input = st.chat_input("Ask me anything about your Puerto Rico trip...")
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
    with st.expander("📜 View Chat Logs", expanded=True):
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
