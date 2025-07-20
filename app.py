import torch
from fastapi import FastAPI, Request
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
from fastapi.middleware.cors import CORSMiddleware

model_id = 'Qwen/Qwen2.5-3B-Instruct'
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
device = 'cpu'
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map='cpu',
    torch_dtype=torch.float16,
    trust_remote_code=True
).to(device)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for local dev; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptInput(BaseModel):
    prompt: dict

@app.post('/chat')
def chat(prompt_input: PromptInput):
    prompt = prompt_input.prompt
    messages = prompt.get("messages", [])
    temperature = prompt.get("temperature", 0.0)
    max_tokens = prompt.get("max_tokens", 100)
    # top_p = prompt.get("top_p", 1.0)
    # top_k = prompt.get("top_k", 0)
    # repetition_penalty = prompt.get("repetition_penalty", 1.0)
    # stop_sequences = prompt.get("stop_sequences", [])

    chat_prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(chat_prompt, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    outputs = model.generate(
        **inputs,
        # top_p=top_p,
        # top_k=top_k,
        # repetition_penalty=repetition_penalty,
        # stop_sequences=stop_sequences,
        max_new_tokens=max_tokens,
        temperature=temperature,
        do_sample=temperature > 0
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    result = response.split(chat_prompt)[-1].strip()
    return {"response": [line.strip() for line in result.strip().splitlines() if line.strip()][-1]}
