# YouTube API Setup Guide

## Prerequisites

1. **Google Cloud Project**: You need a Google Cloud Project with the YouTube Data API enabled
2. **OAuth Credentials**: Create OAuth 2.0 Client ID credentials
3. **client_secret.json**: Download the credentials file

## Step-by-Step Setup

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the YouTube Data API v3:
   - Go to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"

### 2. Create OAuth Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Configure OAuth consent screen if prompted
4. Select "Desktop application" as application type
5. Download the `client_secret.json` file

### 3. Place Credentials File
1. Create a `credentials/` folder in your project root
2. Place the downloaded `client_secret.json` file in `credentials/client_secret.json`

### 4. Authorize Application
Run the setup command:
```bash
python app/main.py --setup-credentials
```

This will:
- Open a browser window with Google's authorization page
- Prompt you to sign in and grant permissions
- Save the credentials for future automated use

## Automated Uploads

Once credentials are set up, the system will automatically upload videos when processing is complete. The credentials are saved securely and will refresh automatically.

## Troubleshooting

- **"client_secret.json not found"**: Make sure the file is in the `credentials/` folder
- **Authentication errors**: Re-run `--setup-credentials` if credentials expire
- **Upload failures**: Check your Google Cloud project quotas and permissions

## Security Notes

- Never commit `client_secret.json` or `token.pickle` to version control
- The `credentials/` folder is in `.gitignore` for security
- Credentials are stored locally and only used for YouTube uploads