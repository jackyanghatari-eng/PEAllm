#!/usr/bin/env python3
"""Continuous training pipeline for PEAllm"""

import os
import schedule
import time
from datetime import datetime
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from datasets import Dataset
from huggingface_hub import login, HfApi

def get_expanded_datasets():
    """Get expanded training datasets"""
    base_data = [
        "EGAT operates 54 power plants with 16,261 MW capacity",
        "鉊葡鉊??鉊?鉆葡鉊?鉊耜腺鉊艇鉊毯?鉆葦鉆?鉊腦鉊啤?鉊落鉆?鉊?鉊﹤葭鉆腦鉊?鉊?鉆葡 54 鉆葦鉆?",
        "MEA serves 4.3 million customers in Bangkok",
        "鉊葡鉊??鉊?鉆葡鉊?鉊?葦鉊丞葷鉊?鉊徇?鉊腦鉊毯?鉊耜腦 4.3 鉊丞?鉊耜?鉊?葡鉊?,
        "PEA provides electricity to 74 provinces",
        "鉊葡鉊??鉊?鉆葡鉊芹?鉊抉?鉊號鉊﹤葩鉊葡鉊?鉊徇?鉊腦鉊毯?鉊耜腦 74 鉊萵鉊葦鉊抉萵鉊?,
        "AEDP targets 30% renewable energy by 2036",
        "鉆?鉊?AEDP 鉆鉊?鉊耜葦鉊﹤葡鉊Ｒ?鉊丞萵鉊?鉊耜?鉊徇腹鉊詮?鉆鉊抉葭鉊Ｒ? 30%",
        "Thailand energy consumption 140,000 ktoe annually",
        "鉊葡鉊??鉊?鉊艇鉊晤?鉊葡鉊?鉊冢?鉆?鉊?140,000 鉊萵鉊?鉊晤?鉆鉊葭鉊Ｒ?鉆鉊?鉊耜?鉆董鉊﹤萵鉊?鉊毯?",
        "ERC regulates electricity and energy markets in Thailand",
        "鉊?鉊? 鉊葷鉊?鉊詮腹鉊艇鉊耜?鉆?鉊?鉊耜?鉊丞萼鉊艇鉊晤?鉊葡鉊?鉊?鉊?萼鉆鉊落鉆?鉊?,
        "PTT is Thailand's national oil and gas company",
        "鉊?鉊? 鉆鉊?鉊?鉊?葩鉊拈萵鉊?鉆董鉊﹤萵鉊?鉊丞萼鉊?鉊耜?鉆葦鉆?鉊葡鉊葩鉊葉鉊?鉊腺",
        "Thailand aims for carbon neutrality by 2050",
        "鉊腦鉊啤?鉊落鉆?鉊Ｒ?鉊晤?鉊?鉊?鉊耜?鉊?鉊?鉊耜腦鉆?鉊冢?鉊葩鉊抉?鉊?萵鉊丞?鉊耜腺鉆?鉊葭 2050",
        "DEDE promotes alternative energy development",
        "鉊腦鉊﹤?鉊晤?鉊葡鉊艇鉊晤?鉊葡鉊?鉊?鉊?鉆艇鉊啤葉鉊虜鉊?萵鉊萱鉆?鉊丞萵鉊?鉊耜?",
        "Net zero emissions target by 2065 for Thailand",
        "鉆鉊?鉊耜葦鉊﹤葡鉊Ｒ?鉊耜腦鉊艇鉆葉鉊Ｒ?鉆葡鉊?鉊?虞鉊冢?鉊腦鉊啤?鉊葵鉊詮?鉊葩鉆鉊?鉊落鉊嫩?鉊Ｒ?鉊葡鉊Ｒ?鉊?鉊?2065"
    ]
    
    return base_data

def train_model_version(version_name):
    """Train a new version of PEAllm"""
    print(f"Starting training for {version_name}")
    
    # Login to HuggingFace
    hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HF_API_TOKEN")
    if not hf_token:
        raise RuntimeError("Set HF_TOKEN or HF_API_TOKEN before running this script.")
    login(token=hf_token)
    
    try:
        # Use the latest version if it exists, otherwise use base model
        try:
            model_name = "jackyanghxc/PEAllm"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            print(f"Loaded existing PEAllm model for fine-tuning")
        except:
            model_name = "Sakjay/Thai-Llama3-8b"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            tokenizer.pad_token = tokenizer.eos_token
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            print(f"Loaded base model {model_name}")
        
        # Prepare training data
        texts = get_expanded_datasets()
        formatted = [f"<|begin_of_text|>{t}<|end_of_text|>" for t in texts]
        dataset = Dataset.from_dict({"text": formatted})
        
        def tokenize(examples):
            return tokenizer(examples["text"], truncation=True, padding=True, max_length=512)
        
        tokenized = dataset.map(tokenize, batched=True)
        
        # Training arguments
        args = TrainingArguments(
            output_dir=f"./peallm-{version_name}",
            num_train_epochs=2,  # Reduced for continuous training
            per_device_train_batch_size=1,
            learning_rate=2e-5,  # Lower learning rate for fine-tuning
            fp16=True,
            logging_steps=5,
            save_steps=10,
            evaluation_strategy="no"
        )
        
        # Create trainer
        trainer = Trainer(
            model=model,
            args=args,
            train_dataset=tokenized,
            data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
        )
        
        # Train model
        print("Training...")
        trainer.train()
        trainer.save_model(f"./PEAllm-{version_name}")
        
        # Upload to HuggingFace
        print("Uploading to HuggingFace...")
        model.push_to_hub("jackyanghxc/PEAllm")
        tokenizer.push_to_hub("jackyanghxc/PEAllm")
        
        print(f"??Successfully trained and uploaded {version_name}")
        return True
        
    except Exception as e:
        print(f"??Error in training {version_name}: {str(e)}")
        return False

def daily_training():
    """Run daily training"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    version_name = f"daily_{timestamp}"
    print(f"\n{'='*50}")
    print(f"Daily Training Started: {datetime.now()}")
    print(f"Version: {version_name}")
    print(f"{'='*50}\n")
    
    success = train_model_version(version_name)
    
    if success:
        print(f"\n??Daily training completed successfully: {version_name}")
        
        # Log training completion
        log_entry = f"{datetime.now()}: Successfully trained {version_name}\n"
        with open("training_log.txt", "a", encoding="utf-8") as f:
            f.write(log_entry)
    else:
        print(f"\n??Daily training failed: {version_name}")
        
        # Log training failure
        log_entry = f"{datetime.now()}: Failed to train {version_name}\n"
        with open("training_log.txt", "a", encoding="utf-8") as f:
            f.write(log_entry)

def setup_scheduler():
    """Setup training scheduler"""
    # Schedule daily training at 2 AM
    schedule.every().day.at("02:00").do(daily_training)
    
    print("?? Training scheduler setup:")
    print("- Daily training at 2:00 AM")
    print("- Logs saved to training_log.txt")
    print("- Press Ctrl+C to stop")

def main():
    """Main continuous training loop"""
    setup_scheduler()
    
    print(f"\n?? PEAllm Continuous Training Started: {datetime.now()}")
    
    # Initialize log file
    with open("training_log.txt", "a", encoding="utf-8") as f:
        f.write(f"\n=== Training Log Started: {datetime.now()} ===\n")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n?對?  Training scheduler stopped by user")
        with open("training_log.txt", "a", encoding="utf-8") as f:
            f.write(f"Training scheduler stopped: {datetime.now()}\n")

if __name__ == "__main__":
    main()
