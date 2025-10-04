from __future__ import annotations

import re
from datetime import datetime
from typing import Dict, Iterable, List, Tuple

SUSPECT_PATTERNS = [
    re.compile(r"\b\d{13}\b"),  # Thai national ID
    re.compile(r"\b\d{10}\b"),  # phone numbers
    re.compile(r"\b[\w.-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
]


def flag_personal_data(value: str) -> bool:
    text = value or ""
    for pattern in SUSPECT_PATTERNS:
        if pattern.search(text):
            return True
    return False


def sanitize_documents(records: Iterable[Dict[str, str]]) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    sanitized: List[Dict[str, str]] = []
    compliance_notes: List[Dict[str, str]] = []

    for record in records:
        flagged_fields = [field for field, value in record.items() if isinstance(value, str) and flag_personal_data(value)]
        if flagged_fields:
            compliance_notes.append(
                {
                    "record_hash": record.get("Content_Hash", ""),
                    "flagged_fields": ",".join(flagged_fields),
                    "observed_at": datetime.utcnow().isoformat(),
                    "action": "excluded",
                }
            )
            continue

        sanitized.append(record)

    return sanitized, compliance_notes


def build_compliance_report(notes: List[Dict[str, str]]) -> str:
    if not notes:
        return "No PDPA risks detected during this run."

    lines = ["record_hash,flagged_fields,observed_at,action"]
    for entry in notes:
        lines.append(
            f"{entry.get('record_hash','')},{entry.get('flagged_fields','')},{entry.get('observed_at','')},{entry.get('action','')}"
        )
    return "\n".join(lines)
