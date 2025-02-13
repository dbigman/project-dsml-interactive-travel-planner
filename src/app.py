import streamlit as st
import openai

# Read API key from file
api_key_path = "API_Key.txt"
with open(api_key_path, "r") as file:
    OPENAI_API_KEY = file.read().strip()

openai.api_key = OPENAI_API_KEY

# Streamlit UI
st.title("Welcome! How can I assist you today?")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant and very knowlegable about Puerto Rico."}]

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

    # Call OpenAI API
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Use "gpt-4" if needed
            messages=st.session_state.messages,
        )
        model_reply = response.choices[0].message.content  
    except Exception as e:
        model_reply = f"Error: {e}"

    # Append AI response
    st.session_state.messages.append({"role": "assistant", "content": model_reply})

    # Display AI response
    with st.chat_message("assistant"):
        st.markdown(model_reply)

