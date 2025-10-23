"""
OAuth2 authentication for Gmail API.
"""
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """
    Authenticate and return Gmail API service.

    Uses environment variables GOOGLE_OAUTH2_CLIENT_ID and
    GOOGLE_OAUTH2_CLIENT_SECRET if set, otherwise falls back
    to credentials.json file.

    Returns:
        googleapiclient.discovery.Resource: Authenticated Gmail service
    """
    creds = None
    token_path = 'token.json'

    # Check if we have saved credentials
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # If credentials don't exist or are invalid, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Check for environment variables first
            client_id = os.environ.get('GOOGLE_OAUTH2_CLIENT_GMAIL_TOOLS_ID')
            client_secret = os.environ.get('GOOGLE_OAUTH2_CLIENT_GMAIL_TOOLS_SECRET')

            if client_id and client_secret:
                # Use environment variables
                client_config = {
                    "installed": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "redirect_uris": ["http://localhost"]
                    }
                }
                flow = InstalledAppFlow.from_client_config(
                    client_config, SCOPES)
            else:
                # Fall back to credentials.json
                credentials_path = 'credentials.json'
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError(
                        f"'{credentials_path}' not found and environment variables "
                        "GOOGLE_OAUTH2_CLIENT_ID and GOOGLE_OAUTH2_CLIENT_SECRET not set. "
                        "Please set the environment variables or download credentials.json "
                        "from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES)

            creds = flow.run_local_server(port=0)

        # Save credentials for future use
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)
