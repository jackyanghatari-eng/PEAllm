#!/usr/bin/env python3
"""Monitor PEAllm training and deployment status"""

import os
import time
from datetime import datetime

def check_status():
    """Check the current status of PEAllm project"""
    print("PEAllm Project Status Monitor")
    print("=" * 50)
    print(f"Status Check Time: {datetime.now()}")
    print()
    
    # Check training completion
    model_exists = os.path.exists("./PEAllm-v1")
    print(f"Model Training: {'COMPLETED' if model_exists else 'IN PROGRESS'}")
    
    # Check if training output directory exists
    training_output = os.path.exists("./peallm-output")
    print(f"Training Output: {'EXISTS' if training_output else 'NOT FOUND'}")
    
    # Check deployment files
    deployment_files = {
        "app.py": "Gradio App",
        "requirements.txt": "Dependencies",
        "README.md": "Documentation", 
        "upload_peallm.py": "Upload Script",
        "deploy_space.py": "Space Deploy Script",
        "continuous_training.py": "Continuous Training"
    }
    
    print("\nDeployment Files:")
    for file, desc in deployment_files.items():
        exists = os.path.exists(file)
        status = "READY" if exists else "MISSING"
        print(f"  {desc}: {status}")
    
    # Check for training logs
    log_exists = os.path.exists("training_log.txt")
    print(f"\nTraining Log: {'EXISTS' if log_exists else 'NOT FOUND'}")
    
    if log_exists:
        try:
            with open("training_log.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    print("  Last log entry:", lines[-1].strip())
        except:
            print("  Could not read log file")
    
    print("\nNext Steps:")
    if not model_exists:
        print("  - Waiting for training to complete...")
    else:
        print("  - Training completed!")
        print("  - Upload model to HuggingFace")
        print("  - Deploy Gradio Space") 
        print("  - Start continuous training pipeline")
    
    print("=" * 50)

if __name__ == "__main__":
    try:
        while True:
            check_status()
            print("\nPress Ctrl+C to stop monitoring")
            print("Next check in 60 seconds...\n")
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nStatus monitoring stopped.")