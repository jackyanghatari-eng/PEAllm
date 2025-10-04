from __future__ import annotations

import argparse

from google_auth_oauthlib.flow import InstalledAppFlow

from automation.gdrive import SCOPES


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Google OAuth refresh token for Drive API access.")
    parser.add_argument("client_id", help="Google OAuth client ID")
    parser.add_argument("client_secret", help="Google OAuth client secret")
    args = parser.parse_args()

    client_config = {
        "installed": {
            "client_id": args.client_id,
            "client_secret": args.client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"]
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent")

    if not creds.refresh_token:
        raise SystemExit("No refresh token returned. Ensure offline access is enabled for the OAuth client.")

    print("\nSave this refresh token as GOOGLE_REFRESH_TOKEN in your GitHub secrets:")
    print(creds.refresh_token)


if __name__ == "__main__":
    main()
