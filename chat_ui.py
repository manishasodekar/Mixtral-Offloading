import streamlit as st
import asyncio
import websockets

# Set the WebSocket URL for the FastAPI server
WS_URL = "ws://localhost:8989/livechat"

st.title("Real-time Chat with Mixtral")

# Initialize WebSocket connection state and chat history
if 'websocket' not in st.session_state:
    st.session_state['websocket'] = None
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'connected' not in st.session_state:
    st.session_state['connected'] = False

# User input
user_input = st.text_input("You: ", "")


# Function to start WebSocket connection
async def start_connection():
    if st.session_state['websocket'] is None or not st.session_state['connected']:
        try:
            st.session_state['websocket'] = await websockets.connect(WS_URL)
            st.session_state['connected'] = True
            st.session_state['history'].append("Connected to the WebSocket.")
        except Exception as e:
            st.session_state['history'].append(f"Connection failed: {e}")
            st.session_state['connected'] = False


# Function to close WebSocket connection
async def close_connection():
    if st.session_state['websocket'] is not None:
        await st.session_state['websocket'].close()
        st.session_state['connected'] = False
        st.session_state['history'].append("Disconnected from the WebSocket.")
        st.session_state['websocket'] = None


# Function to send message and receive tokens
async def send_message():
    if st.session_state['connected']:
        try:
            # Send user input to the server
            await st.session_state['websocket'].send(user_input)

            # Receive tokens and stream them in real-time
            async for message in st.session_state['websocket']:
                st.session_state['history'].append(f"Mixtral: {message}")
                st.experimental_rerun()  # Update the UI with new messages

        except Exception as e:
            st.session_state['history'].append(f"Error during communication: {e}")
            await close_connection()


# Button to initiate WebSocket connection
if not st.session_state['connected']:
    if st.button("Start Chat"):
        asyncio.run(start_connection())

# Button to send the user message
if st.session_state['connected']:
    if user_input and st.button("Send"):
        # Append user input to chat history
        st.session_state['history'].append(f"You: {user_input}")
        asyncio.run(send_message())

# Button to break WebSocket connection
if st.session_state['connected']:
    if st.button("End Chat"):
        asyncio.run(close_connection())

# Display chat history
for message in st.session_state['history']:
    st.write(message)
