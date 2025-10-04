from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    from google.oauth2.service_account import Credentials as ServiceAccountCredentials
    from google.oauth2.credentials import Credentials as OAuthCredentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
except Exception:  # pragma: no cover - optional dependency
    ServiceAccountCredentials = None  # type: ignore
    OAuthCredentials = None  # type: ignore
    Request = None  # type: ignore
    build = None  # type: ignore
    MediaFileUpload = None  # type: ignore

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
TOKEN_URI = "https://oauth2.googleapis.com/token"


class GoogleDriveClient:
    """Best-effort Google Drive wrapper used by the automation pipeline."""

    def __init__(
        self,
        service_account_file: Optional[Path] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ) -> None:
        self.service = None

        # Try Service Account credentials first
        if service_account_file and ServiceAccountCredentials and build:
            creds = ServiceAccountCredentials.from_service_account_file(str(service_account_file), scopes=SCOPES)
            self.service = build("drive", "v3", credentials=creds)
            return

        # Fall back to OAuth client credentials if everything is present
        if all([client_id, client_secret, refresh_token]) and OAuthCredentials and build and Request:
            creds = OAuthCredentials(
                token=None,
                refresh_token=refresh_token,
                token_uri=TOKEN_URI,
                client_id=client_id,
                client_secret=client_secret,
                scopes=SCOPES,
            )
            creds.refresh(Request())
            self.service = build("drive", "v3", credentials=creds)
            return

        # Otherwise, operate in no-op mode (uploads return None).
        if any([service_account_file, client_id, client_secret, refresh_token]):
            print("[WARN] Google Drive credentials incomplete; skipping Drive uploads.")

    def upload_file(self, file_path: Path, folder_id: Optional[str], mime_type: str = "application/json") -> Optional[str]:
        if not self.service or not folder_id or not MediaFileUpload:
            return None

        metadata = {"name": file_path.name, "parents": [folder_id]}
        media = MediaFileUpload(str(file_path), mimetype=mime_type, resumable=True)
        request = self.service.files().create(body=metadata, media_body=media, fields="id, webViewLink")
        response = request.execute()
        return response.get("webViewLink")

