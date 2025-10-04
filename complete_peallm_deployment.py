#!/usr/bin/env python3
"""Complete PEAllm deployment pipeline"""

import os
import time
import subprocess
from huggingface_hub import HfApi, login

def check_model_exists():
    """Check if the trained model exists"""
    return os.path.exists("./PEAllm-v1")

def upload_model():
    """Upload the trained model to HuggingFace"""
    print("Uploading PEAllm model to HuggingFace...")
    try:
        result = subprocess.run(["python", "upload_peallm.py"], capture_output=True, text=True)
        if result.returncode == 0:
            print("Model uploaded successfully")
            return True
        else:
            print(f"Model upload failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error running model upload: {str(e)}")
        return False

def deploy_space():
    """Deploy the HuggingFace Space"""
    print("Deploying HuggingFace Space...")
    try:
        result = subprocess.run(["python", "deploy_space.py"], capture_output=True, text=True)
        if result.returncode == 0:
            print("Space deployed successfully")
            return True
        else:
            print(f"Space deployment failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error running space deployment: {str(e)}")
        return False

def start_continuous_training():
    """Start the continuous training pipeline"""
    print("Starting continuous training pipeline...")
    try:
        # Start continuous training in background
        subprocess.Popen(["python", "continuous_training.py"])
        print("Continuous training pipeline started")
        return True
    except Exception as e:
        print(f"Error starting continuous training: {str(e)}")
        return False

def main():
    """Main deployment pipeline"""
    print("PEAllm Complete Deployment Pipeline")
    print("=" * 50)
    
    # Wait for training to complete
    print("Waiting for model training to complete...")
    while not check_model_exists():
        print("Training still in progress... (checking every 60 seconds)")
        time.sleep(60)
    
    print("Model training completed!")
    
    # Step 1: Upload model
    if upload_model():
        print("Step 1 complete: Model uploaded to HuggingFace")
    else:
        print("Step 1 failed: Model upload")
        return
    
    # Step 2: Deploy Space
    if deploy_space():
        print("Step 2 complete: HuggingFace Space deployed")
    else:
        print("Step 2 failed: Space deployment")
        return
    
    # Step 3: Start continuous training
    if start_continuous_training():
        print("Step 3 complete: Continuous training pipeline started")
    else:
        print("Step 3 failed: Continuous training setup")
        return
    
    print("\nPEAllm Deployment Complete!")
    print("-" * 50)
    print("Model trained and uploaded to HuggingFace")
    print("Gradio Space deployed")
    print("Continuous training pipeline active")
    print("\nLinks:")
    print("Model: https://huggingface.co/jackyanghxc/PEAllm")
    print("Demo: https://huggingface.co/spaces/jackyanghxc/PEAllm-Demo")
    print("\nYour Thailand Energy AI Assistant is now live!")

if __name__ == "__main__":
    main()