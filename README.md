---
title: PEAllm - Thailand Energy AI Assistant
emoji: 🌏
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
---

# 🌏 PEAllm - Thailand Energy AI Assistant

**PEAllm (Provincial Electricity Authority LLM)** is an AI assistant specialized in Thailand's energy sector, trained on data from major Thai energy organizations.

## ℹ️ About

PEAllm is fine-tuned from [Sakjay/Thai-Llama3-8b](https://huggingface.co/Sakjay/Thai-Llama3-8b) to provide accurate information about Thailand's energy landscape in both Thai and English languages.

## 🏢 Covered Organizations

- **EGAT** - Electricity Generating Authority of Thailand
- **MEA** - Metropolitan Electricity Authority
- **PEA** - Provincial Electricity Authority
- **EPPO** - Energy Policy and Planning Office
- **DEDE** - Department of Alternative Energy Development
- **ERC** - Energy Regulatory Commission
- **PTT** - PTT Public Company Limited
- **MOE** - Ministry of Energy

## ❓ What You Can Ask

- Power generation capacity and statistics
- Electricity distribution and coverage
- Renewable energy policies and targets
- Energy consumption data
- Regulatory information
- Oil & gas sector information
- Energy transition plans

## ✨ Features

- **Bilingual**: Supports both Thai (ไทย) and English
- **Specialized**: Trained specifically on Thailand energy sector data
- **PDPA Compliant**: Uses only publicly available information
- **Real-time**: Provides up-to-date energy sector insights

## 📚 Example Questions

- "Tell me about EGAT's power generation capacity"
- "MEA ให้ข้อมูลลูกค้าอย่างไร?"
- "What is Thailand's renewable energy target?"
- "แผน AEDP คืออะไร?"

## 🛠️ Technical Details

- **Base Model**: Sakjay/Thai-Llama3-8b
- **Architecture**: Llama 3 8B
- **Training**: Fine-tuned with LoRA
- **Languages**: Thai + English
- **Framework**: Transformers, PyTorch

## 📄 License

MIT License

## 👤 Created By

**Jack Yang** (@jackyanghxc)
- Email: jackyang.hatari@gmail.com
- HuggingFace: [@jackyanghxc](https://huggingface.co/jackyanghxc)

---

*Made with ❤️ for Thailand's energy sector*

## Automation Pipeline

- **Entry point**: `python -m automation.pipeline` orchestrates scraping, PDPA screening, Drive uploads, Hugging Face dataset sync, and (optionally) remote training triggers.
- **Artifacts**: Generated files land under `automation_artifacts/` before being pushed to Google Drive and Hugging Face.
- **Secrets required**: `HF_API_TOKEN`, `HF_DATASET_REPO_ID`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`, `GOOGLE_DRIVE_RAW_FOLDER_ID`, `GOOGLE_DRIVE_PROCESSED_FOLDER_ID`, `GOOGLE_DRIVE_PDPA_FOLDER_ID` (optional: `GOOGLE_SERVICE_ACCOUNT_JSON`; training hook: `HF_TRAINING_TRIGGER_URL`, `HF_TRAINING_TRIGGER_METHOD`, `HF_TRAINING_TRIGGER_PAYLOAD`, `HF_TRAINING_TRIGGER_TIMEOUT`).
- **Local run**: Export the env vars above (`GOOGLE_SERVICE_ACCOUNT_FILE` optional) then execute the entry point. Place your Google service-account JSON at `service-account.json` in the repo root or set the env var to its path.
- **Trigger remote training**: Define `HF_TRAINING_TRIGGER_URL` (AutoTrain webhook or custom API). The pipeline POSTs the dataset metadata using your `HF_API_TOKEN`.
- **Generate refresh token**: Run `python automation/get_refresh_token.py <CLIENT_ID> <CLIENT_SECRET>` once, copy the printed refresh token into your GitHub secrets as `GOOGLE_REFRESH_TOKEN`.

### GitHub Actions

- Workflow: `.github/workflows/data_pipeline.yml` runs every 6 hours or manually.
- Add the secrets listed above in your repository settings before enabling the schedule.
- Each run uploads the sanitized dataset to `jackyanghxc/peallm-poc` and archives reports as workflow artifacts.

### Remote Training

- Configure a Hugging Face AutoTrain (or Training Jobs) project targeting `jackyanghxc/peallm-poc` as the dataset.
- Copy the project webhook URL and store it as `HF_TRAINING_TRIGGER_URL`. Provide optional JSON overrides via `HF_TRAINING_TRIGGER_PAYLOAD` (e.g. `{ "job": "daily" }`).
- When the GitHub Action runs, it publishes the latest dataset shard and then hits the webhook so AutoTrain fine-tunes Sakjay/Thai-Llama3-8b and pushes adapters to `jackyanghxc/PEAllm`.
- Monitor AutoTrain logs; successful runs rebuild the Space to serve the newest weights.
