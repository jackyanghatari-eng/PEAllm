from __future__ import annotations

import json
from typing import Any, Dict, Optional

import requests


def trigger_training(
    url: str,
    token: Optional[str],
    method: str = "POST",
    payload: Optional[str] = None,
    timeout: int = 60,
    dataset_repo: Optional[str] = None,
    processed_file: Optional[str] = None,
) -> Dict[str, Any]:
    if not url:
        raise ValueError("Training trigger URL is required")

    headers = {"User-Agent": "PEAllm-Automation/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    json_payload: Dict[str, Any] = {}
    if payload:
        if payload.strip().startswith("{"):
            json_payload = json.loads(payload)
        else:
            raise ValueError("HF_TRAINING_TRIGGER_PAYLOAD must be a JSON object string")

    if dataset_repo and "dataset_repo" not in json_payload:
        json_payload["dataset_repo"] = dataset_repo
    if processed_file and "processed_file" not in json_payload:
        json_payload["processed_file"] = processed_file

    response = requests.request(
        method=method.upper(),
        url=url,
        headers=headers,
        json=json_payload or None,
        timeout=timeout,
    )
    response.raise_for_status()

    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "text": response.text[:500]}
