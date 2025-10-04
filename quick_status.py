#!/usr/bin/env python3
"""Quick PEAllm status check"""

import os
from datetime import datetime

print("PEAllm Project Status")
print("=" * 30)
print(f"Time: {datetime.now()}")
print()

# Check training completion
model_exists = os.path.exists("./PEAllm-v1")
print(f"Model Training: {'COMPLETED' if model_exists else 'IN PROGRESS'}")

# Check training output
training_output = os.path.exists("./peallm-output")  
print(f"Training Output: {'EXISTS' if training_output else 'NOT FOUND'}")

# Check key files
files = ["app.py", "requirements.txt", "README.md", "upload_peallm.py", "deploy_space.py"]
print("\nKey Files:")
for file in files:
    exists = "OK" if os.path.exists(file) else "MISSING"
    print(f"  {file}: {exists}")

print("\nProject Status:")
if model_exists:
    print("  Ready for deployment!")
else:
    print("  Training in progress...")