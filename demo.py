import re

from constants import state_path, model_name, quantized_model_name
from transformers import AutoConfig, AutoTokenizer, TextStreamer
import torch
from build_model_state import model, device
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel

# Initialize tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_name)
past_key_values = None

app = FastAPI()


class ChatInput(BaseModel):
    user_input: str
    output_len: int


class ChatOutput(BaseModel):
    text: str
    response: int


class WebSocketStreamer(TextStreamer):
    def __init__(self, tokenizer, websocket, skip_prompt=True, skip_special_tokens=True):
        super().__init__(tokenizer, skip_prompt=skip_prompt, skip_special_tokens=skip_special_tokens)
        self.websocket = websocket

    async def on_token(self, token):
        """Override the on_token method to send the token to WebSocket."""
        try:
            await self.websocket.send_text(token)  # Send token to the websocket client
            print(f"Sent token: {token}")  # Debug statement
        except Exception as e:
            print(f"Error sending token: {e}")


@app.post("/chat", response_model=ChatOutput)
async def chat(input: ChatInput):
    user_input = input.user_input
    user_entry = dict(role="user", content=user_input)
    input_ids = tokenizer.apply_chat_template([user_entry], return_tensors="pt").to(device)

    attention_mask = torch.ones_like(input_ids)

    result = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        past_key_values=None,
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
    filtered_text = re.sub(r'\[INST\].*?\[/INST\]', '', decoded_text, flags=re.DOTALL).strip()
    return ChatOutput(text=filtered_text, response=token_count)


@app.websocket("/livechat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    chat_history = []
    past_key_values = None
    while True:
        try:
            user_input = await websocket.receive_text()
            print(f"Received user input: {user_input}")  # Debug statement
            user_entry = dict(role="user", content=user_input)
            chat_history.append(user_entry)

            input_ids = tokenizer.apply_chat_template(chat_history, return_tensors="pt").to(device)

            user_input_ids = tokenizer(user_input, return_tensors="pt").input_ids
            user_input_length = user_input_ids.size(1)
            max_new_tokens = max(user_input_length * 2, 256)

            attention_mask = torch.ones_like(input_ids)

            # Initialize the WebSocketStreamer
            streamer = WebSocketStreamer(tokenizer, websocket)

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

            sequence = result["sequences"]
            past_key_values = result.get("past_key_values", None)

            generated_text = tokenizer.decode(sequence[0], skip_special_tokens=True)
            filtered_text = re.sub(r'\[INST\].*?\[/INST\]', '', generated_text, flags=re.DOTALL).strip()
            await websocket.send_text(filtered_text)
            assistant_entry = dict(role="assistant", content=generated_text.strip())
            chat_history.append(assistant_entry)

        except Exception as e:
            print(f"Error: {e}")
            await websocket.close()
            break
