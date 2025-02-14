import streamlit as st
import subprocess
import time
import openai
import os
import logging
import sys
from dotenv import load_dotenv
import json
import datetime
from icecream import ic
import chromadb
import streamlit.components.v1 as components



# -------------------------------------------------------------------
# 1. Start the Flask server as a background process
# -------------------------------------------------------------------
flask_process = subprocess.Popen(["python", "maps_app.py"])
time.sleep(2)  # Give the Flask server a moment to start up

ic.disable()

# -------------------------------------------------------------------
# 2. Logging Setup
# -------------------------------------------------------------------
logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.hasHandlers():
    logger.handlers.clear()

file_handler = logging.FileHandler("chatbot_correction.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.info("Logging initialized.")

# -------------------------------------------------------------------
# 3. Load Environment Variables & Setup OpenAI
# -------------------------------------------------------------------
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logger.error("OpenAI API key is missing! Check your .env file.")
    raise ValueError("OpenAI API key not found.")

openai.api_key = openai_api_key
openai.api_type = "openai"
logger.info("OpenAI configuration set. API type: openai.")

# -------------------------------------------------------------------
# 4. Setup a Single ChromaDB Client and Load Collections
# -------------------------------------------------------------------
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

municipalities_collection = load_chromadb_collection(client, "municipalities")
news_collection = load_chromadb_collection(client, "news_articles")
landmarks_collection = load_chromadb_collection(client, "landmarks")

# Quick check
if news_collection:
    docs = news_collection.get()
    ic(f"Documents in collection 'news_articles':", docs)

# -------------------------------------------------------------------
# 5. Helper Functions for Retrieval and Chat
# -------------------------------------------------------------------
def retrieve_relevant_info(query, collection):
    logger.info(f"Querying collection for query: {query}")
    results = collection.query(query_texts=[query], n_results=3)
    logger.info(f"Query results: {results}")
    return results

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
        ic(context)
    
    combined_context_parts = []
    for docs in context:
        if docs and "documents" in docs:
            logger.info("docs['documents'] content: " + str(docs["documents"]))
            # Flatten if needed (some versions of ChromaDB return a list-of-lists)
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
            f"""{user_input}\n\n
            Please answer using your travel planning expertise about Puerto Rico. When a location is mentioned, 
            provide a bullet list of landmarks with their GPS coordinates. 
            """
        )
        system_message = """
        You are a helpful travel planner assistant for Puerto Rico. Use only the provided context.
        The end result of a successful interaction with an interested user should be a list of landmarks
        of interest for the user. The list of landmarks should include gps coordinates and a brief description. 
        """
        
        logger.info("No context found, using general travel planning prompt.")
    else:
        prompt = (
            f"{user_input}\n\n"
            f"Context:\n{combined_context}\n\n"
            "Answer using only the provided context."
        )
        system_message = "You are a helpful travel planner assistant for Puerto Rico. Use only the provided context."
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_completion_tokens=250,
            top_p=1,
            frequency_penalty=1,
            presence_penalty=-1
        )
        model_reply = response.choices[0].message.content
        logger.info("Received model reply: " + model_reply)
        log_chat(user_input, model_reply)
        ic(model_reply)
        return model_reply
    except Exception as e:
        logger.error(f"Error in chat_with_llm: {e}")
        return f"Error: {e}"

# -------------------------------------------------------------------
# 6. Streamlit UI Setup
# -------------------------------------------------------------------

# Initialize chat session
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Welcome to your Puerto Rico Travel Planner! How can I help you plan your trip today?"
    })
    logger.info("Added intro msg to chat history.")

# Define three columns: left, center, right
# col_left, col_center, col_right = st.columns([1, 3, 1])
# Define three columns: left, center, right

st.set_page_config(layout="wide")
col_left, col_center, col_right = st.columns([1, 4, 1])

with col_left:
    st.write("")

# -------------------------
# Center Column with Chat
# -------------------------
with col_center:
    # Inject CSS for a scrollable chat area with the input pinned at the bottom.
    st.markdown(
        """
        <style>
        /* Container that holds messages + input */
        /* Remove padding from main block */
        .main .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
        }
            .chat-messages {
                max-height: 100vh;
                overflow-y: auto;
                margin-bottom: 0rem;
            }
        </style>
        <div class="center-column">
        <div class="chat-messages">
        """,
        unsafe_allow_html=True
    )

    # Show existing chat messages in the scrollable area
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Close the chat-messages div
    st.markdown("</div>", unsafe_allow_html=True)

    # Now place the chat input, which stays visually at bottom
    user_input = st.chat_input("Ask me anything about Puerto Rico...")
    if user_input:
        logger.info("User input received: " + user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        model_reply = chat_with_llm(user_input)
        st.session_state.messages.append({"role": "assistant", "content": model_reply})
        logger.info("Assistant reply appended to session state.")
        # Immediately display the model's response so user sees it
        with st.chat_message("assistant"):
            st.markdown(model_reply)

    # Close the center-column container
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Right Column with Map
# -------------------------
with col_right:
    # You can label it if you like:
    st.write("**Interactive Map**")
    components.iframe("http://localhost:5000", height=400, width=300, scrolling=True)

# -------------------------
# Sidebar for Chat Logs
# -------------------------
with st.sidebar:
    st.markdown("### Chat Logs")
    with st.expander("View Chat Logs", expanded=True):
        try:
            if os.path.exists("chat_logs.jsonl"):
                with open("chat_logs.jsonl", "r", encoding="utf-8") as log_file:
                    logs = log_file.read()
                st.text_area("Chat Logs", logs, height=400, max_chars=5000)
                logger.info("Chat logs displayed in dashboard.")
            else:
                st.write("No chat logs found.")
        except Exception as e:
            st.error("Error loading chat logs: " + str(e))
            logger.error("Error loading chat logs: " + str(e))
