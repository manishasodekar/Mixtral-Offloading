# Mixtral-Offloading

This repository provides a setup for the Mixtral offloading project, including an API call for generating responses and
a Svelte-based chat UI.

## API Call

To interact with the Mixtral API, you can use `curl` to send a POST request. Below is an example of how to make an API
call:

```bash
    curl --location --request POST 'https://localhost:8080/mixtral/chat' \
    --header 'Content-Type: application/json' \
    --data '{
        "user_input": "Write the recipe for a chicken curry with coconut milk.",
        "output_len": 100
    }'
```


## Chat UI

This repository includes a simple chat interface built with Svelte, which can be used to interact with the Mixtral API. The chat interface is located in the `svelte-chat-app` directory.

### Steps to Run the Chat UI:

1. Navigate to the `svelte-chat-app` directory:

    ```bash
    cd svelte-chat-app
    ```

2. Install the necessary dependencies:

    ```bash
    npm install
    ```

3. Start the development server:

    ```bash
    npm run dev
    ```

4. Open your browser and go to `http://localhost:5000` to use the chat interface.

---

### How the Chat UI Works:

- The chat UI allows users to input their queries, which are then sent to the Mixtral API.
- The UI will display the response returned by the API in real-time, creating a smooth conversational experience.

---

### Development:

- Ensure that you have Node.js installed.
- Modify the `App.svelte` or other components under the `svelte-chat-app/src` folder to customize the chat UI.
- If you wish to deploy the chat UI, build the project using:

    ```bash
    npm run build
    ```

This will generate a `public` folder with all the static assets that can be hosted on a server.

---

### Troubleshooting:

- **Port Issues**: If the app fails to start or reports a port conflict, edit the port in `rollup.config.js` or use an environment variable to set a different port.
- **Dependencies**: Ensure all required dependencies are installed by running `npm install`. If problems persist, try removing the `node_modules` folder and reinstalling:

    ```bash
    rm -rf node_modules
    npm install
    ```

