<script>
    import { onMount } from 'svelte';

    let ws;
    let message = "";
    let messages = [];
    let chatWindow;

    // Function to safely convert newlines to <br> tags
    const formatMessage = (text) => {
        return text.replace(/\n/g, '<br>');
    };

    // Scroll chat window to the bottom
    const scrollToBottom = () => {
        if (chatWindow) {
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }
    };

    // Mock function to simulate Mixtral's response
    const simulateMixtralResponse = (userMessage) => {
        setTimeout(() => {
            messages = [...messages, { sender: "Mixtral", text: formatMessage(userMessage) }];
            scrollToBottom(); // Scroll down after adding new message
        }, 1000);
    };

    // Function to handle WebSocket disconnection
    const handleWebSocketClose = () => {
        // Post a "session expired" message when the WebSocket is closed
        messages = [...messages, { sender: "System", text: "Session expired." }];
        scrollToBottom(); // Scroll down after posting the message
    };

    const connectWebSocket = () => {
        ws = new WebSocket("wss://fluidstack-3090-1.healiom-service.com/mixtral/livechat");

        ws.onmessage = (event) => {
            // Assume all WebSocket messages are from Mixtral
            simulateMixtralResponse(event.data);
        };

        ws.onclose = () => {
            console.log("Connection closed");
            handleWebSocketClose();
        };

        // Close WebSocket after 10 minutes (600,000 milliseconds)
        setTimeout(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.close();
            }
        }, 600000); // 10 minutes
    };

    const sendMessage = () => {
        if (message.trim() !== "") {
            // Immediately add the user's message to the chat window
            messages = [...messages, { sender: "User", text: formatMessage(message) }];
            scrollToBottom(); // Scroll down after adding new message

            // Send the message via WebSocket
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(message);
            } else {
                messages = [...messages, { sender: "System", text: "Cannot send message, session expired." }];
                scrollToBottom(); // Scroll down if sending fails
            }

            // Clear the input field
            message = "";
        }
    };

    onMount(() => {
        connectWebSocket();
    });
</script>

<main>
    <div id="chat-container">
        <h1>Chat Application</h1>

        <div id="chat-window" bind:this={chatWindow}>
            {#each messages as msg}
                <div class={msg.sender === 'User' ? 'user-message' : (msg.sender === 'Mixtral' ? 'mixtral-message' : 'system-message')}>
                    <!-- Using {@html} to safely render multiline text -->
                    <p><strong>{msg.sender}: </strong><span>{@html msg.text}</span></p>
                </div>
            {/each}
        </div>

        <div id="input-container">
            <input
                bind:value={message}
                on:keypress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Type a message..."
            />
            <button on:click={sendMessage}>Send</button>
        </div>
    </div>
</main>

<style>
    body {
        font-family: Arial, sans-serif;
        background-color: #ece5dd;
        margin: 0;
        padding: 0;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
    }

    #chat-container {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        width: 100%;
        max-width: 600px;
        height: 80vh; /* Use 80% of viewport height */
        margin: 0 auto;
        border-radius: 10px;
        overflow: hidden;
        background-color: #fff;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }

    h1 {
        text-align: center;
        background-color: #075e54;
        color: white;
        margin: 0;
        padding: 10px;
        font-size: 1.5rem;
    }

    #chat-window {
        flex-grow: 1;
        padding: 10px;
        overflow-y: auto;
        background-color: #e5ddd5;
        height: 100%; /* Make the chat window fill available space */
    }

    #input-container {
        display: flex;
        align-items: center;
        padding: 10px;
        background-color: #fff;
        border-top: 1px solid #ccc;
    }

    input {
        flex: 1;
        padding: 10px;
        border: none;
        border-radius: 20px;
        margin-right: 10px;
        font-size: 1rem;
        background-color: #f0f0f0;
    }

    button {
        padding: 10px 20px;
        background-color: #25d366;
        color: white;
        border: none;
        border-radius: 20px; /* Rounded corners */
        font-size: 1rem;
        cursor: pointer;
        text-align: center;
    }

    .user-message {
        text-align: right;
        margin-bottom: 10px;
    }

    .mixtral-message {
        text-align: left;
        margin-bottom: 10px;
    }

    .system-message {
        text-align: center;
        margin-bottom: 10px;
        color: red;
        font-style: italic;
    }

    .user-message p, .mixtral-message p {
        display: inline-block;
        padding: 10px;
        border-radius: 10px;
        max-width: 80%;
        word-wrap: break-word;
    }

    .user-message p {
        background-color: #dcf8c6;
    }

    .mixtral-message p {
        background-color: #fff;
    }

    #chat-window::-webkit-scrollbar {
        width: 8px;
    }

    #chat-window::-webkit-scrollbar-thumb {
        background-color: rgba(0, 0, 0, 0.2);
        border-radius: 4px;
    }

    /* Media queries for responsiveness */

    /* Large Laptops (1440px and larger) */
    @media (min-width: 1440px) {
        #chat-container {
            max-width: 800px; /* Larger width for bigger screens */
            height: 85vh; /* Increased height for large screens */
        }

        h1 {
            font-size: 2rem;
        }

        button {
            padding: 12px 24px;
            font-size: 1.1rem;
        }

        input {
            font-size: 1.1rem;
        }
    }

    /* Laptops (1024px to 1440px) */
    @media (min-width: 1024px) and (max-width: 1440px) {
        #chat-container {
            max-width: 700px; /* Moderate width for laptop screens */
            height: 85vh; /* Increased height for laptop screens */
        }

        h1 {
            font-size: 1.8rem;
        }

        button {
            padding: 10px 20px;
            font-size: 1.05rem;
        }

        input {
            font-size: 1.05rem;
        }
    }

    /* Tablets and larger phones (portrait and landscape) */
    @media (max-width: 768px) {
        #chat-container {
            max-width: 100%;
            border-radius: 0;
            height: 90vh;
        }

        h1 {
            font-size: 1.2rem;
        }

        button {
            padding: 8px 16px;
            font-size: 0.9rem;
        }

        input {
            font-size: 0.9rem;
        }

        #chat-window {
            height: 100%;
        }
    }

    /* Phones (landscape) */
    @media (max-width: 576px) {
        #chat-container {
            max-width: 100%;
            border-radius: 0;
            height: 95vh;
        }

        h1 {
            font-size: 1.1rem;
        }

        button {
            padding: 6px 12px;
            font-size: 0.8rem;
        }

        input {
            font-size: 0.8rem;
        }

        #chat-window {
            height: 100%;
        }
    }

    /* Phones (portrait) */
    @media (max-width: 480px) {
        #chat-container {
            max-width: 100%;
            border-radius: 0;
            height: 95vh;
        }

        h1 {
            font-size: 1rem;
        }

        button {
            padding: 5px 10px;
            font-size: 0.75rem;
        }

        input {
            font-size: 0.75rem;
        }

        #chat-window {
            height: 100%;
        }
    }
</style>
