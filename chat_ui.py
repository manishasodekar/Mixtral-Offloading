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


async def start_connection():
    if st.session_state['websocket'] is None or not st.session_state['connected']:
        try:
            st.session_state['websocket'] = await websockets.connect(WS_URL)
            st.session_state['connected'] = True
            st.session_state['history'].append("Connected to the WebSocket.")
        except Exception as e:
            st.session_state['history'].append(f"Connection failed: {e}")
            st.session_state['connected'] = False


async def close_connection():
    if st.session_state['websocket'] is not None:
        await st.session_state['websocket'].close()
        st.session_state['connected'] = False
        st.session_state['history'].append("Disconnected from the WebSocket.")
        st.session_state['websocket'] = None


async def send_message():
    if st.session_state['connected']:
        try:
            # Send user input to the server
            await st.session_state['websocket'].send(user_input)

            # Receive tokens and stream them in real-time
            async for message in st.session_state['websocket']:
                st.session_state['history'].append(f"Mixtral: {message}")
                # Use st.experimental_rerun() carefully to avoid performance issues
                st.experimental_rerun()

        except Exception as e:
            st.session_state['history'].append(f"Error during communication: {e}")
            await close_connection()


# Start chat button
if st.button("Start Chat") and not st.session_state['connected']:
    # Create an asyncio task to run the start_connection function
    asyncio.create_task(start_connection())

# Send button
if st.session_state['connected'] and user_input:
    if st.button("Send"):
        # Append user input to chat history
        st.session_state['history'].append(f"You: {user_input}")
        # Create an asyncio task to run the send_message function
        asyncio.create_task(send_message())

# End chat button
if st.session_state['connected']:
    if st.button("End Chat"):
        # Create an asyncio task to run the close_connection function
        asyncio.create_task(close_connection())

# Display chat history
for message in st.session_state['history']:
    st.write(message)
