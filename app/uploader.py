import os
import pickle
import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# Required scope for uploading videos
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

CREDENTIALS_DIR = "credentials"
CLIENT_SECRET_FILE = os.path.join(CREDENTIALS_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(CREDENTIALS_DIR, "token.pickle")


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
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE,
                SCOPES
            )
            creds = flow.run_console()

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
