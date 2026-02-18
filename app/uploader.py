import os
import pickle
import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# Required scope for uploading videos
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

CREDENTIALS_DIR = "credentials"
CLIENT_SECRET_FILE = os.path.join(CREDENTIALS_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(CREDENTIALS_DIR, "token.pickle")


def check_credentials_status():
    """
    Check if YouTube API credentials are properly set up.

    Returns:
        dict: Status information with 'valid', 'message', and 'needs_setup' keys
    """
    if not os.path.exists(CLIENT_SECRET_FILE):
        return {
            'valid': False,
            'needs_setup': True,
            'message': f"client_secret.json not found in {CREDENTIALS_DIR}. Follow YOUTUBE_SETUP.md to set up credentials."
        }

    if not os.path.exists(TOKEN_FILE):
        return {
            'valid': False,
            'needs_setup': True,
            'message': "YouTube credentials not set up. Run: python app/main.py --setup-credentials"
        }

    try:
        # Try to load and validate credentials
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

        if creds and creds.valid:
            return {
                'valid': True,
                'needs_setup': False,
                'message': "Credentials are valid and ready for uploads."
            }
        elif creds and creds.expired and creds.refresh_token:
            # Try to refresh
            creds.refresh(Request())
            # Save refreshed credentials
            with open(TOKEN_FILE, "wb") as token:
                pickle.dump(creds, token)
            return {
                'valid': True,
                'needs_setup': False,
                'message': "Credentials refreshed successfully."
            }
        else:
            return {
                'valid': False,
                'needs_setup': True,
                'message': "Credentials expired. Run: python app/main.py --setup-credentials"
            }
    except Exception as e:
        return {
            'valid': False,
            'needs_setup': True,
            'message': f"Error loading credentials: {e}. Run: python app/main.py --setup-credentials"
        }


def setup_credentials():
    print("Setting up YouTube API credentials...")
    print("Make sure you have:")
    print("1. Created a Google Cloud Project")
    print("2. Enabled YouTube Data API v3")
    print("3. Created OAuth 2.0 Client ID credentials")
    print("4. Downloaded client_secret.json to credentials/ folder")
    print()

    if not os.path.exists(CLIENT_SECRET_FILE):
        raise FileNotFoundError(f"client_secret.json not found in {CREDENTIALS_DIR}")

    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        SCOPES
    )

    creds = flow.run_local_server(port=0)

    # Save credentials for future use
    with open(TOKEN_FILE, "wb") as token:
        pickle.dump(creds, token)

    print(f"Credentials saved to {TOKEN_FILE}")
    print("You can now use automated uploads!")


def get_authenticated_service():
    creds = None

    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("No valid credentials found. Starting authentication...")
            print("For automated uploads, you need to:")
            print("1. Go to: https://console.developers.google.com/")
            print("2. Create a project or select existing one")
            print("3. Enable YouTube Data API v3")
            print("4. Create OAuth 2.0 credentials")
            print("5. Download client_secret.json to credentials/ folder")
            print("6. Run this once manually to authorize, then it will be automated")
            print()

            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE,
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save credentials for future use
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)


def upload_video(
    file_path,
    title,
    description="",
    tags=None,
    privacy_status="private",
    publish_in_hours=None
):
    """
    Uploads a video to YouTube.

    Args:
        file_path (str): Path to video file
        title (str): Video title
        description (str): Video description
        tags (list): List of tags
        privacy_status (str): 'public', 'private', or 'unlisted'
        publish_in_hours (int): Schedule publish X hours from now (optional)
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Video file not found: {file_path}")

    youtube = get_authenticated_service()

    if tags is None:
        tags = []

    # Ensure Shorts hashtag is included
    if "#shorts" not in description.lower():
        description += "\n\n#shorts"

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22"  # People & Blogs
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }

    # Handle scheduled publishing
    if publish_in_hours is not None:
        publish_time = (
            datetime.datetime.utcnow() +
            datetime.timedelta(hours=publish_in_hours)
        ).isoformat("T") + "Z"

        body["status"]["privacyStatus"] = "private"
        body["status"]["publishAt"] = publish_time

    try:
        print("Uploading video...")

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=MediaFileUpload(
                file_path,
                chunksize=-1,
                resumable=True
            )
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Upload progress: {int(status.progress() * 100)}%")

        print("Upload complete.")
        print(f"Video ID: {response['id']}")

        return response

    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        raise

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
