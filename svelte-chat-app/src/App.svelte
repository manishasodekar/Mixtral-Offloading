<script>
    let ws;
    let message = "";
    let messages = [];

    const connectWebSocket = () => {
        ws = new WebSocket("wss://fluidstack-3090-1.healiom-service.com/mixtral/livechat");

        ws.onmessage = (event) => {
            messages = [...messages, event.data];
        };

        ws.onclose = () => {
            console.log("Connection closed");
        };
    };

    const sendMessage = () => {
        if (ws && message.trim() !== "") {
            ws.send(message);
            message = "";
        }
    };

    connectWebSocket();
</script>

<main>
    <h1>Chat Application</h1>

    <div id="chat-window">
        {#each messages as msg}
            <p>{msg}</p>
        {/each}
    </div>

    <input
        bind:value={message}
        on:keypress={(e) => e.key === 'Enter' && sendMessage()}
        placeholder="Type a message..."
    />

    <button on:click={sendMessage}>Send</button>
</main>

<style>
    #chat-window {
        height: 300px;
        border: 1px solid #ccc;
        padding: 10px;
        overflow-y: auto;
        margin-bottom: 10px;
    }
    input {
        width: calc(100% - 60px);
        padding: 8px;
        margin-right: 10px;
    }
</style>
