# YouTube Cookies Setup for Age-Restricted Videos

## Problem
YouTube age-restricted videos require authentication to access certain formats. Without cookies, yt-dlp may fail to download these videos with errors like:
```
[youtube] xWXHDXxAZOk: This video is age-restricted; some formats may be missing without authentication.
```

## Solutions

### Option 1: Browser Cookies (Recommended - Automatic)
The system automatically tries to use cookies from your browser:

1. **Make sure you're logged into YouTube** in Chrome or Firefox
2. The system will automatically detect and use your browser cookies
3. No manual setup required!

**Supported Browsers:**
- Chrome/Chromium
- Firefox
- Edge
- Safari
- Opera

### Option 2: Export Cookies to File (Manual Setup)

If automatic browser cookie detection doesn't work, you can manually export cookies:

#### Step 1: Install Cookie Export Extension
**For Chrome:**
1. Install "Get cookies.txt" extension from Chrome Web Store
2. Or use "Cookie-Editor" extension

**For Firefox:**
1. Install "Export Cookies" extension
2. Or use "Cookie Quick Manager"

#### Step 2: Export YouTube Cookies
1. Go to YouTube.com and log in
2. Click the cookie export extension
3. Export cookies in Netscape format
4. Save as `cookies/cookies.txt` in your project directory

#### Step 3: Verify Setup
```bash
python app/main.py --check-cookies
```

## Cookie File Location
Place your cookie file at:
```
cookies/cookies.txt
```

The system will automatically detect and use this file.

## Troubleshooting

### "No cookies found" message
- Ensure you're logged into YouTube in your browser
- Or export cookies manually to `cookies/cookies.txt`

### "Invalid cookie file" error
- Make sure the cookie file is in Netscape format
- Check that the file path is correct: `cookies/cookies.txt`

### Still getting age-restricted errors
- Try refreshing your browser cookies
- Re-export cookies if using manual method
- Check that your YouTube account has access to the content

## Security Notes
- Cookies contain sensitive authentication data
- Never commit `cookies/cookies.txt` to version control
- The `cookies/` folder is in `.gitignore` for security
- Browser cookies are read-only and not stored by the application

## Testing
To test if cookies are working:
```bash
# Try downloading an age-restricted video
python app/main.py --download-url "https://www.youtube.com/watch?v=VIDEO_ID"
```

The system will show which cookie method it's using in the output.