from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from thai_energy_scraper import ThaiEnergyWebScraper

from automation.config import PipelineConfig
from automation.gdrive import GoogleDriveClient
from automation.hf_dataset import HFDatasetSync
from automation.pdpa import build_compliance_report, sanitize_documents
from automation.training import trigger_training


def _write_json(data: List[Dict[str, str]], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_jsonl(data: List[Dict[str, str]], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as stream:
        for row in data:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def run_pipeline(timestamp: Optional[str] = None) -> Dict[str, Optional[str]]:
    cfg = PipelineConfig.from_env()
    ts = timestamp or datetime.utcnow().strftime("%Y%m%d-%H%M%S")

    scraper = ThaiEnergyWebScraper()
    total_docs = scraper.scrape_all_websites()

    raw_records = scraper.all_documents
    raw_path = cfg.raw_output_dir / f"thai_energy_raw_{ts}.json"
    _write_json(raw_records, raw_path)

    sanitized_records, compliance_notes = sanitize_documents(raw_records)
    processed_path = cfg.processed_output_dir / f"thai_energy_processed_{ts}.jsonl"
    _write_jsonl(sanitized_records, processed_path)

    compliance_report = build_compliance_report(compliance_notes)
    report_path = cfg.compliance_output_dir / f"pdpa_report_{ts}.csv"
    report_path.write_text(compliance_report, encoding="utf-8")

    drive_client = GoogleDriveClient(
        cfg.service_account_file,
        cfg.google_client_id,
        cfg.google_client_secret,
        cfg.google_refresh_token,
    )
    raw_link = drive_client.upload_file(raw_path, cfg.drive_raw_folder_id)
    processed_link = drive_client.upload_file(processed_path, cfg.drive_processed_folder_id, mime_type="application/json")
    report_link = drive_client.upload_file(report_path, cfg.drive_compliance_folder_id, mime_type="text/csv")

    hf_link = None
    repo_path = None
    training_response = None
    try:
        hf_sync = HFDatasetSync(cfg.hf_dataset_repo, cfg.hf_token)
        repo_path = f"processed/{processed_path.name}"
        hf_sync.upload_file(processed_path, repo_path=repo_path)
        hf_link = f"https://huggingface.co/datasets/{cfg.hf_dataset_repo}/blob/main/{repo_path}"
    except Exception as exc:  # pragma: no cover - network credentials required
        print(f"[WARN] Hugging Face upload skipped: {exc}")

    if cfg.hf_training_trigger_url:
        try:
            training_response = trigger_training(
                url=cfg.hf_training_trigger_url,
                token=cfg.hf_token,
                method=cfg.hf_training_method,
                payload=cfg.hf_training_payload,
                timeout=cfg.hf_training_timeout,
                dataset_repo=cfg.hf_dataset_repo,
                processed_file=repo_path if hf_link else str(processed_path.name),
            )
        except Exception as exc:  # pragma: no cover - network credentials required
            print(f"[WARN] Training trigger failed: {exc}")
            training_response = {"error": str(exc)}

    return {
        "timestamp": ts,
        "documents_collected": str(total_docs),
        "raw_file": str(raw_path),
        "processed_file": str(processed_path),
        "pdpa_report": str(report_path),
        "drive_raw_link": raw_link,
        "drive_processed_link": processed_link,
        "drive_report_link": report_link,
        "hf_dataset_link": hf_link,
        "training_trigger_url": cfg.hf_training_trigger_url,
        "training_response": json.dumps(training_response, ensure_ascii=False) if isinstance(training_response, dict) else training_response,
    }


if __name__ == "__main__":
    summary = run_pipeline()
    print(json.dumps(summary, indent=2))




