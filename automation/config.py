from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import os


def _optional(env: os._Environ[str], key: str) -> Optional[str]:
    value = env.get(key)
    if value is None:
        return None
    value = value.strip()
    return value or None


@dataclass
class PipelineConfig:
    raw_output_dir: Path
    processed_output_dir: Path
    compliance_output_dir: Path
    hf_dataset_repo: str
    hf_token: Optional[str]
    drive_raw_folder_id: Optional[str]
    drive_processed_folder_id: Optional[str]
    drive_compliance_folder_id: Optional[str]
    service_account_file: Optional[Path]
    google_client_id: Optional[str]
    google_client_secret: Optional[str]
    google_refresh_token: Optional[str]
    hf_training_trigger_url: Optional[str]
    hf_training_payload: Optional[str]
    hf_training_method: str
    hf_training_timeout: int
    timezone: str

    @classmethod
    def from_env(cls) -> "PipelineConfig":
        env = os.environ
        raw_dir = Path(env.get("PEALLM_RAW_DIR", "automation_artifacts/raw"))
        processed_dir = Path(env.get("PEALLM_PROCESSED_DIR", "automation_artifacts/processed"))
        compliance_dir = Path(env.get("PEALLM_COMPLIANCE_DIR", "automation_artifacts/pdpa"))
        for path in (raw_dir, processed_dir, compliance_dir):
            path.mkdir(parents=True, exist_ok=True)

        service_account_setting = _optional(env, "GOOGLE_SERVICE_ACCOUNT_FILE")
        service_account_path: Optional[Path] = None
        if service_account_setting:
            candidate = Path(service_account_setting)
            if candidate.exists():
                service_account_path = candidate
        else:
            default_sa = Path("service-account.json")
            if default_sa.exists():
                service_account_path = default_sa

        timeout_value = _optional(env, "HF_TRAINING_TRIGGER_TIMEOUT")
        hf_timeout = int(timeout_value) if timeout_value else 60

        return cls(
            raw_output_dir=raw_dir,
            processed_output_dir=processed_dir,
            compliance_output_dir=compliance_dir,
            hf_dataset_repo=env.get("HF_DATASET_REPO_ID", "jackyanghxc/peallm-poc"),
            hf_token=_optional(env, "HF_API_TOKEN"),
            drive_raw_folder_id=_optional(env, "GOOGLE_DRIVE_RAW_FOLDER_ID"),
            drive_processed_folder_id=_optional(env, "GOOGLE_DRIVE_PROCESSED_FOLDER_ID"),
            drive_compliance_folder_id=_optional(env, "GOOGLE_DRIVE_PDPA_FOLDER_ID"),
            service_account_file=service_account_path,
            google_client_id=_optional(env, "GOOGLE_CLIENT_ID"),
            google_client_secret=_optional(env, "GOOGLE_CLIENT_SECRET"),
            google_refresh_token=_optional(env, "GOOGLE_REFRESH_TOKEN"),
            hf_training_trigger_url=_optional(env, "HF_TRAINING_TRIGGER_URL"),
            hf_training_payload=_optional(env, "HF_TRAINING_TRIGGER_PAYLOAD"),
            hf_training_method=_optional(env, "HF_TRAINING_TRIGGER_METHOD") or "POST",
            hf_training_timeout=hf_timeout,
            timezone=env.get("PEALLM_TIMEZONE", "Asia/Bangkok"),
        )
