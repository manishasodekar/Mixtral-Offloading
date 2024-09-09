from constants import state_path, model_name, quantized_model_name
from transformers import AutoConfig, AutoTokenizer, TextStreamer
import torch
from constants import model_name
from build_model_state import model, device
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel

tokenizer = AutoTokenizer.from_pretrained(model_name)
streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
past_key_values = None
sequence = None
seq_len = 0

app = FastAPI()


class ChatInput(BaseModel):
    user_input: str
    output_len: int


class ChatOutput(BaseModel):
    text: str
    response: int


# WebSocket Token Streamer (custom streamer to handle websocket)
class WebSocketStreamer(TextStreamer):
    def __init__(self, tokenizer, websocket, skip_prompt=True, skip_special_tokens=True):
        super().__init__(tokenizer, skip_prompt=skip_prompt, skip_special_tokens=skip_special_tokens)
        self.websocket = websocket

    async def on_token(self, token):
        """Override the on_token method to send the token to WebSocket."""
        await self.websocket.send_text(token)  # Send token to the websocket client


@app.post("/chat", response_model=ChatOutput)
async def chat(input: ChatInput):
    user_input = input.user_input
    user_entry = dict(role="user", content=user_input)
    input_ids = tokenizer.apply_chat_template([user_entry], return_tensors="pt").to(device)

    # if past_key_values is None:
    attention_mask = torch.ones_like(input_ids)
    # else:
    #   seq_len = input_ids.size(1) + past_key_values[0][0][0].size(1)
    #   attention_mask = torch.ones([1, seq_len - 1], dtype=torch.int, device=device)

    result = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        past_key_values=None,
        # streamer=streamer,
        do_sample=True,
        temperature=0.9,
        top_p=0.9,
        max_new_tokens=input.output_len,
        pad_token_id=tokenizer.eos_token_id,
        return_dict_in_generate=True,
        output_hidden_states=True,
    )

    sequence = result["sequences"]
    decoded_text = tokenizer.decode(sequence[0], skip_special_tokens=True)
    token_count = len(sequence[0])
    return ChatOutput(text=decoded_text, response=token_count)


@app.websocket("/livechat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    past_key_values = None
    chat_history = []
    while True:
        try:
            # Receive the user's input from the client
            user_input = await websocket.receive_text()
            print("user_input", user_input)
            # Prepare the input for the model
            user_entry = dict(role="user", content=user_input)
            chat_history.append(user_entry)

            input_ids = tokenizer.apply_chat_template(chat_history, return_tensors="pt").to(device)

            # Get the length of user input in tokens
            user_input_ids = tokenizer(user_input, return_tensors="pt").input_ids
            user_input_length = user_input_ids.size(1)

            # Dynamically calculate max_new_tokens (for example, 2x the user input length)
            max_new_tokens = min(user_input_length * 2, 256)  # Limit max_new_tokens to a reasonable size (e.g., 256)

            attention_mask = torch.ones_like(input_ids)

            # Use the WebSocketStreamer to send tokens as they are generated
            streamer = WebSocketStreamer(tokenizer, websocket)

            # Generate the response token-by-token and stream it
            result = model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                past_key_values=past_key_values,
                streamer=streamer,
                do_sample=True,
                temperature=1,
                top_p=0.9,
                max_new_tokens=max_new_tokens,
                pad_token_id=tokenizer.eos_token_id,
                return_dict_in_generate=True,
                output_hidden_states=True,
            )

            # Extract sequences and past_key_values for subsequent turns
            sequence = result["sequences"]
            # past_key_values = result["past_key_values"]

            # Stream each token as it's generated
            generated_text = tokenizer.decode(sequence[0], skip_special_tokens=True)
            assistant_entry = dict(role="assistant", content=generated_text.strip())
            chat_history.append(assistant_entry)

        except Exception as e:
            print(f"Error: {e}")
            await websocket.close()
            break
