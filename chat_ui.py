import streamlit as st
import asyncio
import websockets

WEBSOCKET_URL = "wss://fluidstack-3090-1.healiom-service.com/mixtral/livechat"


# Async function to initialize the WebSocket
async def initialize_websocket():
    if 'websocket' not in st.session_state or st.session_state.websocket is None or st.session_state.websocket.closed:
        try:
            st.session_state.websocket = await websockets.connect(WEBSOCKET_URL)
            st.session_state.websocket_open = True
        except Exception as e:
            st.error(f"Failed to connect to WebSocket: {e}")
            st.session_state.websocket_open = False


# Async function to close the WebSocket connection
async def close_websocket():
    if 'websocket' in st.session_state and st.session_state.websocket and not st.session_state.websocket.closed:
        try:
            await st.session_state.websocket.close()
            st.session_state.websocket_open = False
        except Exception as e:
            st.error(f"An error occurred while closing the WebSocket: {e}")


# Async function to send and receive messages from WebSocket
async def fetch_data(message):
    if st.session_state.websocket_open:
        try:
            await st.session_state.websocket.send(message)
            response = await st.session_state.websocket.recv()
            return response
        except Exception as e:
            return f"Error while communicating with WebSocket: {e}"
    else:
        return "WebSocket connection is not open."


# Wrapper to handle async message fetching
def get_data(message):
    return asyncio.run(fetch_data(message))


# Initialize WebSocket connection when the page loads
if 'websocket_open' not in st.session_state:
    st.session_state.websocket_open = False
    asyncio.run(initialize_websocket())  # Initialize WebSocket on page load

# Streamlit app UI
st.title("WebSocket Chat with WebSocket Initialization on Page Load")

# Create a sidebar for chat messages
with st.sidebar:
    messages = st.container()

# Main content for chat input
with st.container():
    if prompt := st.chat_input("Say something"):
        try:
            # Send the user input and get the response
            response = get_data(prompt)

            # Display user and assistant messages
            with messages:
                st.chat_message("user").write(prompt)
                st.chat_message("assistant").write(f"Echo: {response}")

        except Exception as e:
            st.error(f"An error occurred: {e}")

# Clean up WebSocket on app close/refresh
if st.session_state.websocket_open:
    try:
        asyncio.run(close_websocket())
    except Exception as e:
        st.error(f"An error occurred while closing the WebSocket: {e}")
