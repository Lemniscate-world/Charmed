import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/documents']

# The ID of the Google Document you want to update (from the URL)
# Example URL: https://docs.google.com/document/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
# The ID is: 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
DOCUMENT_ID = 'YOUR_DOCUMENT_ID_HERE'
SOURCE_FILE = "../SESSION_SUMMARY.md"

def get_credentials():
    creds = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def sync_to_google_docs():
    """Syncs the content of SESSION_SUMMARY.md to a given Google Doc."""
    try:
        if not os.path.exists(SOURCE_FILE):
            print(f"Error: Could not find {SOURCE_FILE}")
            return

        with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

        creds = get_credentials()
        service = build('docs', 'v1', credentials=creds)

        # First, clear the existing document (optional, but good for a full sync)
        # Or we can just append, but here we'll append to the top for recent first.

        requests = [
            {
                'insertText': {
                    'location': {
                        'index': 1,
                    },
                    'text': content + "\n\n---\n\n"
                }
            }
        ]

        result = service.documents().batchUpdate(
            documentId=DOCUMENT_ID, body={'requests': requests}).execute()

        print(f"Successfully synced {SOURCE_FILE} to Google Docs!")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Make sure you have downloaded 'credentials.json' from the Google Cloud Console.")

if __name__ == '__main__':
    sync_to_google_docs()
