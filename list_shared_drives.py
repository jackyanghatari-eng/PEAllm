from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from pathlib import Path

SERVICE_ACCOUNT_FILE = Path('service-account.json')

scopes = ['https://www.googleapis.com/auth/drive.readonly']
creds = Credentials.from_service_account_file(str(SERVICE_ACCOUNT_FILE), scopes=scopes)
drive = build('drive', 'v3', credentials=creds)

drive_list = drive.drives().list(pageSize=100).execute()
drives = drive_list.get('drives', [])
if not drives:
    print('No shared drives visible to service account.')
else:
    for d in drives:
        print(f"{d['name']}\t{d['id']}")
