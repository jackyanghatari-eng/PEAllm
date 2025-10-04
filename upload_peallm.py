#!/usr/bin/env python3
"""Upload trained PEAllm model to HuggingFace Hub"""

import os
from huggingface_hub import HfApi, login
from transformers import AutoTokenizer, AutoModelForCausalLM

def upload_model():
    """Upload the trained PEAllm model to HuggingFace"""
    
    # Login to HuggingFace
    hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HF_API_TOKEN")
    if not hf_token:
        raise RuntimeError("Set HF_TOKEN or HF_API_TOKEN before running this script.")
    login(token=hf_token)
    
    # Model details
    model_path = "./PEAllm-v1"
    repo_id = "jackyanghxc/PEAllm"
    
    print(f"Uploading model from {model_path} to {repo_id}")
    
    try:
        # Load the model and tokenizer
        model = AutoModelForCausalLM.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained("Sakjay/Thai-Llama3-8b")
        
        # Push to hub
        model.push_to_hub(repo_id)
        tokenizer.push_to_hub(repo_id)
        
        print(f"??Successfully uploaded PEAllm to https://huggingface.co/{repo_id}")
        
        # Create model card
        model_card = f"""---
license: mit
base_model: Sakjay/Thai-Llama3-8b
tags:
- thai
- llama3
- energy
- thailand
- pea
- egat
- mea
language:
- th
- en
---

# PEAllm - Thailand Energy AI Assistant

PEAllm (Provincial Electricity Authority LLM) is a specialized AI model for Thailand's energy sector, fine-tuned from Sakjay/Thai-Llama3-8b.

## Model Details

- **Base Model**: Sakjay/Thai-Llama3-8b
- **Domain**: Thailand Energy Sector
- **Languages**: Thai + English
- **Training Data**: 40+ bilingual energy sector samples
- **Organizations Covered**: EGAT, MEA, PEA, EPPO, DEDE, ERC, PTT, MOE

## Usage

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("jackyanghxc/PEAllm")
model = AutoModelForCausalLM.from_pretrained("jackyanghxc/PEAllm")

# Generate response
prompt = "Tell me about EGAT's power generation capacity"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=100)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
```

## Training Details

- **Fine-tuning Method**: Standard fine-tuning
- **Epochs**: 3
- **Learning Rate**: 5e-5
- **Batch Size**: 1
- **Max Length**: 512 tokens

## Covered Topics

- Power generation capacity and statistics
- Electricity distribution networks
- Renewable energy policies and targets
- Energy consumption data
- Regulatory framework
- Oil & gas sector information

## Created By

**Jack Yang** (@jackyanghxc)
- Email: jackyang.hatari@gmail.com

## License

MIT License
"""
        
        # Upload model card
        api = HfApi()
        api.upload_file(
            path_or_fileobj=model_card.encode(),
            path_in_repo="README.md",
            repo_id=repo_id,
            commit_message="Add model card for PEAllm"
        )
        
        print("??Model card uploaded successfully")
        return True
        
    except Exception as e:
        print(f"??Error uploading model: {str(e)}")
        return False

if __name__ == "__main__":
    success = upload_model()
    if success:
        print("?? PEAllm model upload completed!")
    else:
        print("? Model upload failed!")
