# EXECUTE PEAllm TRAINING NOW
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from datasets import Dataset
from huggingface_hub import login


def get_datasets():
    return [
        "EGAT operates 54 power plants with 16,261 MW capacity",
        "การไฟฟ้าฝ่ายผลิตแห่งประเทศไทยมีโรงไฟฟ้า 54 แห่ง",
        "MEA serves 4.3 million customers in Bangkok",
        "การไฟฟ้านครหลวงให้บริการลูกค้า 4.3 ล้านรายในกรุงเทพฯ",
        "PEA provides electricity to 74 provinces",
        "การไฟฟ้าส่วนภูมิภาคดูแลไฟฟ้า 74 จังหวัด",
        "AEDP targets 30% renewable energy by 2036",
        "แผน AEDP ตั้งเป้าพลังงานหมุนเวียน 30% ภายในปี 2579",
        "Thailand energy consumption 140,000 ktoe annually",
        "การใช้พลังงานขั้นสุดท้ายของไทย 140,000 พันตันเทียบเท่าน้ำมันต่อปี"
    ]


print("STARTING PEALLM TRAINING")
hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HF_API_TOKEN")
if not hf_token:
    raise RuntimeError("Set HF_TOKEN or HF_API_TOKEN in your environment before running training.")
login(token=hf_token)

tokenizer = AutoTokenizer.from_pretrained("Sakjay/Thai-Llama3-8b")
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    "Sakjay/Thai-Llama3-8b",
    torch_dtype=torch.float16,
    low_cpu_mem_usage=True,
    offload_folder="./offload"
)

texts = get_datasets()
formatted = [f"<|begin_of_text|>{t}<|end_of_text|>" for t in texts]
dataset = Dataset.from_dict({"text": formatted})


def tokenize(examples):
    return tokenizer(examples["text"], truncation=True, padding=True, max_length=512)


tokenized = dataset.map(tokenize, batched=True)

args = TrainingArguments(
    output_dir="./peallm-output",
    num_train_epochs=3,
    per_device_train_batch_size=1,
    learning_rate=5e-5,
    fp16=True,
    logging_steps=5
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized,
    data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
)

print("TRAINING...")
trainer.train()
trainer.save_model("./PEAllm-v1")
print("DONE - PEAllm-v1 SAVED")
