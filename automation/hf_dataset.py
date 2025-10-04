from __future__ import annotations

from pathlib import Path
from typing import Optional

from huggingface_hub import HfApi, HfFolder


class HFDatasetSync:
    def __init__(self, repo_id: str, token: Optional[str] = None):
        self.repo_id = repo_id
        self.token = token or HfFolder.get_token()
        if not self.token:
            raise RuntimeError("Missing Hugging Face token. Set HF_API_TOKEN env var or run huggingface-cli login.")
        self.api = HfApi()

    def upload_file(self, file_path: Path, repo_path: Optional[str] = None) -> None:
        repo_path = repo_path or file_path.name
        self.api.upload_file(
            path_or_fileobj=str(file_path),
            path_in_repo=repo_path,
            repo_id=self.repo_id,
            repo_type="dataset",
            token=self.token,
        )
