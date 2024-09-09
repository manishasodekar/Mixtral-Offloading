from constants import state_path, model_name, quantized_model_name
from transformers import AutoConfig, AutoTokenizer, TextStreamer
import torch
from constants import model_name
from build_model_state import model, device
from fastapi import FastAPI
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
    response: int


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
        streamer=streamer,
        do_sample=True,
        temperature=0.9,
        top_p=0.9,
        max_new_tokens=input.output_len,
        pad_token_id=tokenizer.eos_token_id,
        return_dict_in_generate=True,
        output_hidden_states=True,
    )

    sequence = result["sequences"]
    # decoded_text = tokenizer.decode(sequence[0], skip_special_tokens=True)
    token_count = len(sequence[0])
    return ChatOutput(response=token_count)
