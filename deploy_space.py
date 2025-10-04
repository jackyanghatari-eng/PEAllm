#!/usr/bin/env python3
"""Deploy PEAllm HuggingFace Space"""

import os
from huggingface_hub import HfApi, login

def deploy_space():
    """Deploy the PEAllm Gradio app to HuggingFace Spaces"""
    
    # Login to HuggingFace
    hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HF_API_TOKEN")
    if not hf_token:
        raise RuntimeError("Set HF_TOKEN or HF_API_TOKEN before running this script.")
    login(token=hf_token)
    
    # Space details
    space_id = "jackyanghxc/PEAllm-Demo"
    
    print(f"Creating HuggingFace Space: {space_id}")
    
    try:
        api = HfApi()
        
        # Create the space
        api.create_repo(
            repo_id=space_id,
            repo_type="space",
            space_sdk="gradio",
            exist_ok=True
        )
        
        # Upload files
        files_to_upload = [
            ("app.py", "app.py"),
            ("requirements.txt", "requirements.txt"),
            ("README.md", "README.md")
        ]
        
        for local_file, repo_file in files_to_upload:
            if os.path.exists(local_file):
                print(f"Uploading {local_file} -> {repo_file}")
                api.upload_file(
                    path_or_fileobj=local_file,
                    path_in_repo=repo_file,
                    repo_id=space_id,
                    repo_type="space",
                    commit_message=f"Upload {repo_file}"
                )
            else:
                print(f"??  Warning: {local_file} not found, skipping")
        
        print(f"??Successfully deployed PEAllm Space!")
        print(f"?? Visit your Space at: https://huggingface.co/spaces/{space_id}")
        
        return True
        
    except Exception as e:
        print(f"??Error deploying space: {str(e)}")
        return False

if __name__ == "__main__":
    success = deploy_space()
    if success:
        print("?? PEAllm Space deployment completed!")
    else:
        print("? Space deployment failed!")
