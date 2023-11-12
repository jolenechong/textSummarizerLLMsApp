import requests
import streamlit as st
import time
import random
import os
from dotenv import load_dotenv
import pandas as pd
import base64
load_dotenv()

# get env variables RDS_ENDPOINT
RDS_ENDPOINT = os.getenv("RDS_ENDPOINT")
RDS_ENDPOINT_SUMMARIZE = RDS_ENDPOINT + "/summarize"

# set meta data
st.set_page_config(
    page_title="LLM Summarizer",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="auto",
)

# add side bar
st.sidebar.title("LLM Summarizer")
st.sidebar.info("This is a demo of the LLM Summarizer. You can ask me to summarize anything!")

with st.sidebar.expander("About"):
    st.write("Fine-tuned LLM model for video conference/webinar transcripts summarization.")
    st.write("Built with 🤗 Transformers, Streamlit, and AWS")
    st.write("######")
    st.markdown(
        """<p><strong>About Me<strong><br/>Hi, I'm <a href="https://github.com/jolenechong/">Jolene Chong</a>! I design and build interfaces. I'm passionate about building products that make a positive impact on people's lives with AI.</p>""",
        unsafe_allow_html=True)

# divider
st.sidebar.markdown("---")
st.sidebar.write("Model Details")
# dropdown to select model used
selected_model = st.sidebar.selectbox(
    "",
    ("bart-large", "gpt-3.5", "palm-2"),
    label_visibility="collapsed"
)

if selected_model == "gpt-3.5":
    api_key = st.sidebar.text_input("Enter OpenAI API key", type="password")
elif selected_model == "palm-2":
    api_key = st.sidebar.text_input("Enter GCP API key", type="password")

st.sidebar.write("Summarize a file")
uploaded = st.sidebar.file_uploader("", type=["txt"], label_visibility="collapsed")

def get_table_download_link(messages):
    df = pd.DataFrame(messages)
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    return f'<a href="data:file/csv;base64,{b64}" download="chat_history.csv">Download here</a>'

def summarizeBart(text):
    print('hello')
    try:
        response = requests.get(RDS_ENDPOINT, timeout=2)
        addBotPrompt("Sure! Summarizing...\nThis might take awhile...")
        response = requests.post(
            RDS_ENDPOINT_SUMMARIZE,
            json={"text": text})
        
        addBotPrompt(response.json()['message'])
        return True
    except requests.exceptions.ConnectionError:
        print("Connection refused")
        return False

if uploaded is not None:
    # TODO: update this
    text = uploaded.read().decode("utf-8")
    if selected_model == "bart-large":
        summarizeBart(text)

# download chat history
if st.sidebar.button("Download chat history"):
    st.sidebar.markdown(get_table_download_link(st.session_state.messages), unsafe_allow_html=True)

info = """
Here are some things you can ask me to do:\n
Tell me to summarize something:  
    \tsummarize: <enter text here>  
    \tsummarize: The quick brown fox jumped over the lazy dog.\n
You can also select a different model and upload a transcript as a file to summarize.
"""

def addUserPrompt(prompt):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

def addBotPrompt(response, help=False):
    with st.chat_message("ai"):
        message_placeholder = st.empty()
        full_response = ""
        # Simulate stream of response with milliseconds delay
        for chunk in response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        if help == True:
            st.info(info)
            st.session_state.messages.append({"role": "ai", "content": response + "<<<" + info + ">>>"})
        else:
            st.session_state.messages.append({"role": "ai", "content": response})
        message_placeholder.markdown(full_response)

st.subheader("💬 Summarize")
st.write("Ask me to summarize anything!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # display text within <<<>>> as info box
        if "<<<" in message["content"]:
            info = message["content"].split("<<<")[1].split(">>>")[0]
            text = message["content"].split("<<<")[0]
            st.markdown(text)
            st.info(info)
        else:
            st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Send a message..."):
    if prompt.lower().startswith("hi") or prompt.lower().startswith("hello"):
        addUserPrompt(prompt)
        assistant_response = random.choice(
            [
                "Hello there! How can I assist you today?",
                "Hi, human! Is there anything I can help you with?",
                "Do you need help?",
            ]
        )
        addBotPrompt(assistant_response, help=True)
    elif "summarize:" in prompt.lower():
        # check if server is up
        addUserPrompt(prompt)
        if selected_model == "bart-large":
            if summarizeBart(prompt.lower().split("summarize:")[1].strip()) == False:
                addBotPrompt("Sorry, I'm not available right now. Please try again later.")
        elif selected_model == "gpt-3.5":
            addBotPrompt("NOT IMPLEMENTED YET")
        elif selected_model == "palm-2":
            addBotPrompt("NOT IMPLEMENTED YET")
    elif "use" in prompt.lower():
        modelToUse = prompt.lower().split("use")[1].strip()
        addUserPrompt(prompt)
        addBotPrompt("Sure! I will start using " + modelToUse + "...")
    else:
        addUserPrompt(prompt)
        assistant_response = "Sorry, I don't understand. Could you rephrase?"
        addBotPrompt(assistant_response)