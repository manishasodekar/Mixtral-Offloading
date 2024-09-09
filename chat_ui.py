# WEBSOCKET_URL = "ws://localhost:8989/livechat"
WEBSOCKET_URL = "wss://fluidstack-3090-1.healiom-service.com/mixtral/livechat"

import streamlit as st
import asyncio
import websockets


async def fetch_data(message):
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        await websocket.send(message)  # Send the user input message
        response = await websocket.recv()  # Receive the response
        return response


@st.cache(ttl=600, allow_output_mutation=True)
def get_data(message):
    return asyncio.run(fetch_data(message))


# Create a text input for user message
user_input = st.text_input("Enter your message:")

if user_input:
    # Get data from WebSocket server
    response = get_data(user_input)

    # Initialize or append to the existing chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = ""

    st.session_state.chat_history += f"User: {user_input}\nServer: {response}\n"

    # Display chat history
    st.write(st.session_state.chat_history)
