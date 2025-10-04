import os

# Prevent bitsandbytes from attempting GPU ops on CPU-only builds
os.environ["BITSANDBYTES_NOWELCOME"] = "1"
os.environ["DISABLE_BNB_QUANTIZATION_CHECK"] = "1"

import gradio as gr
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import spaces

MODEL_CANDIDATES = [
    "jackyanghxc/PEAllm",
    "Sakjay/Thai-Llama3-8b"
]


def _select_device_and_dtype():
    """Return device map and dtype based on GPU availability."""
    if torch.cuda.is_available():
        return "cuda", torch.float16
    return "cpu", torch.float32


@spaces.GPU
def load_model():
    """Load tokenizer and model when a GPU worker spins up."""
    device_map, dtype = _select_device_and_dtype()
    last_error = None
    for name in MODEL_CANDIDATES:
        try:
            tokenizer = AutoTokenizer.from_pretrained(name)
            model = AutoModelForCausalLM.from_pretrained(
                name,
                torch_dtype=dtype,
                device_map=device_map,
                low_cpu_mem_usage=True
            )
            model.eval()
            return tokenizer, model
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    raise RuntimeError(f"Failed to load model: {last_error}")


def generate_response(message, history):
    """Generate response from PEAllm."""
    tokenizer, model = load_model()
    try:
        prompt = f"<|begin_of_text|>{message}"
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )
        if torch.cuda.is_available():
            inputs = {k: v.to(model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=200,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )

        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.replace(prompt, "").strip()
    except Exception as exc:  # noqa: BLE001
        return f"Error: {exc}"


title = "PEAllm - Thailand Energy AI Assistant"
description = """
**PEAllm (Provincial Electricity Authority LLM)** – Your AI assistant for Thailand's energy sector.

Ask questions about:
- EGAT (Electricity Generating Authority of Thailand)
- MEA (Metropolitan Electricity Authority)
- PEA (Provincial Electricity Authority)
- EPPO (Energy Policy and Planning Office)
- DEDE (Department of Alternative Energy Development)
- ERC (Energy Regulatory Commission)
- PTT (PTT Public Company Limited)
- Thailand energy policies and statistics

**Languages**: Thai and English
"""

examples = [
    ["Tell me about EGAT's power generation capacity"],
    ["MEA ให้ข้อมูลลูกค้าอย่างไร?"],
    ["What is Thailand's renewable energy target?"],
    ["แผน AEDP คืออะไร?"],
    ["How many provinces does PEA serve?"],
    ["การใช้พลังงานขั้นสุดท้ายของไทยเป็นอย่างไร?"]
]


demo = gr.ChatInterface(
    fn=generate_response,
    title=title,
    description=description,
    examples=examples,
    theme="soft",
)

demo.css = """
.gradio-container {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.chat-message {
    padding: 10px;
    border-radius: 10px;
}
"""


if __name__ == "__main__":
    demo.launch()
