import streamlit as st
import requests
import base64
import json
import os
from dotenv import load_dotenv

# Load the .env file if environment variables are not set
if not os.environ.get("GPT4V_KEY") or not os.environ.get("GPT4V_ENDPOINT"):
    load_dotenv()

# Configuration
GPT4V_KEY = os.environ.get("GPT4V_KEY")
GPT4V_ENDPOINT = os.environ.get("GPT4V_ENDPOINT")

if GPT4V_KEY is None or GPT4V_ENDPOINT is None:
    raise ValueError("GPT4V_KEY or GPT4V_ENDPOINT environment variables are not set")

headers = {
    "Content-Type": "application/json",
    "api-key": GPT4V_KEY,
}

st.title("Azure OpenAI GPT-4o Chat App")

# Define the SessionState class
class SessionState:
    def __init__(self):
        self.user_input = "Hello!"
        self.uploaded_file = None

# Create an instance of SessionState
session_state = SessionState()

session_state.user_input = st.text_input("You:", session_state.user_input)
session_state.uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if st.button("Send"):
    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "You are an AI assistant that helps people find information."
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": session_state.user_input
                }
            ]
        }
    ]

    if session_state.uploaded_file is not None:
        encoded_image = base64.b64encode(session_state.uploaded_file.read()).decode('ascii')
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{encoded_image}"
                    }
                },
                {
                    "type": "text",
                    "text": "What's this?"
                }
            ]
        })

    payload = {
        "messages": messages,
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800
    }

    try:
        response = requests.post(GPT4V_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        response_data = response.json()

        # Extract the assistant's message from the response
        assistant_message = response_data["choices"][0]["message"]["content"]
        st.write("Assistant:", assistant_message)
    except requests.RequestException as e:
        st.error(f"Failed to make the request. Error: {e}")
