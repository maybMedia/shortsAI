import os
import yt_dlp
import re
from datetime import datetime, timedelta

INPUT_DIR = "input_videos"
COOKIES_DIR = "cookies"

def sanitize_filename(filename):
    """Sanitize filename to remove invalid characters"""
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def get_cookie_options():
    """
    Get cookie options for yt-dlp to handle age-restricted videos.

    Returns:
        dict: Cookie options for yt-dlp
    """
    cookie_options = {}

    # Check for cookies.txt file first (most reliable)
    cookies_file = os.path.join(COOKIES_DIR, "cookies.txt")
    if os.path.exists(cookies_file):
        cookie_options['cookiefile'] = cookies_file
        print("Using cookies from cookies.txt for age-restricted content")
        return cookie_options

    # Try to extract cookies from browsers
    browsers_to_try = [
        ('chrome', 'Chrome'),
        ('firefox', 'Firefox'),
        ('edge', 'Edge'),
        ('opera', 'Opera'),
        ('safari', 'Safari'),
    ]

    for browser_code, browser_name in browsers_to_try:
        try:
            cookie_options['cookiesfrombrowser'] = (browser_code,)
            # Test if browser cookies are accessible
            with yt_dlp.YoutubeDL(cookie_options) as ydl:
                ydl.extract_info('https://www.youtube.com', download=False)
            print(f"Using {browser_name} browser cookies for age-restricted content")
            return cookie_options
        except Exception as e:
            # Browser not available or no cookies, try next one
            continue

    # No cookies available
    print("Warning: No cookies found. Age-restricted videos may fail to download.")
    print("To fix this:")
    print("1. Export YouTube cookies: https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies")
    print("2. Save as cookies/cookies.txt")
    print("3. Or ensure you're logged into YouTube in Chrome/Firefox/Edge")
    print("4. Run: python app/main.py --check-cookies")
    return cookie_options

def download_popular_videos(topic, max_videos=5, min_duration=15, max_duration=1200):
    """
    Download popular videos from a given topic.

    Args:
        topic (str): The topic to search for
        max_videos (int): Maximum number of videos to download
        min_duration (int): Minimum video duration in seconds (default: 15)
        max_duration (int): Maximum video duration in seconds (default: 1200 = 20 min)
    """

    # Ensure input directory exists
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(COOKIES_DIR, exist_ok=True)

    # yt-dlp options
    ydl_opts = {
        'format': 'best',  # Get best available quality
        'outtmpl': os.path.join(INPUT_DIR, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        'match_filter': yt_dlp.utils.match_filter_func(
            "!is_live"
        ),
        'postprocessors': [{
            'key': 'FFmpegVideoRemuxer',
            'preferedformat': 'mp4',
        }],
    }

    # Add cookie options for age-restricted content
    cookie_opts = get_cookie_options()
    ydl_opts.update(cookie_opts)

    # Search query for popular videos - make it more specific for certain topics
    search_query = f"ytsearch{max_videos}:{topic}"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Searching for popular videos about: {topic}")
            info_dict = ydl.extract_info(search_query, download=True)

            if 'entries' in info_dict:
                videos = info_dict['entries']
                print(f"Found {len(videos)} videos matching criteria")

                downloaded_count = 0
                for video in videos:
                    if video and downloaded_count < max_videos:
                        title = sanitize_filename(video.get('title', 'Unknown'))
                        duration = video.get('duration', 0)
                        view_count = video.get('view_count', 0)

                        print(f"Downloaded: {title}")
                        print(f"Duration: {duration}s, Views: {view_count:,}")
                        downloaded_count += 1

                print(f"Successfully downloaded {downloaded_count} videos to {INPUT_DIR}")
            else:
                print("No videos found matching the criteria")

    except Exception as e:
        error_msg = str(e)
        if "age-restricted" in error_msg.lower() or "sign in to confirm your age" in error_msg.lower():
            print("❌ Video is age-restricted and cannot be downloaded with current cookie setup.")
            print("To fix this:")
            print("1. Make sure you're logged into YouTube in your browser")
            print("2. Or export YouTube cookies manually: https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies")
            print("3. Save cookies as cookies/cookies.txt")
            print("4. Run: python app/main.py --check-cookies")
            print(f"Original error: {error_msg}")
        else:
            print(f"Error downloading videos: {e}")

def download_trending_videos(max_videos=5, min_duration=30, max_duration=1200):
    """
    Download trending videos from YouTube.

    Args:
        max_videos (int): Maximum number of videos to download
        min_duration (int): Minimum video duration in seconds (default: 30)
        max_duration (int): Maximum video duration in seconds (default: 1200 = 20 min)
    """

    # Ensure input directory exists
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(COOKIES_DIR, exist_ok=True)

    # yt-dlp options
    ydl_opts = {
        'format': 'best[height<=720]',
        'outtmpl': os.path.join(INPUT_DIR, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        'match_filter': yt_dlp.utils.match_filter_func(
            f"!is_live & duration > {min_duration} & duration < {max_duration}"
        ),
        'postprocessors': [{
            'key': 'FFmpegVideoRemuxer',
            'preferedformat': 'mp4',
        }],
    }

    # Add cookie options for age-restricted content
    cookie_opts = get_cookie_options()
    ydl_opts.update(cookie_opts)

    # Search for trending videos (recent popular videos)
    # Using search query that finds videos with high view counts
    search_query = f"ytsearch{max_videos * 3}:trending"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Searching for trending videos...")
            info_dict = ydl.extract_info(search_query, download=True)

            if 'entries' in info_dict:
                videos = info_dict['entries']
                print(f"Found {len(videos)} trending videos")

                downloaded_count = 0
                for video in videos:
                    if video and downloaded_count < max_videos:
                        title = sanitize_filename(video.get('title', 'Unknown'))
                        duration = video.get('duration', 0)
                        view_count = video.get('view_count', 0)

                        print(f"Downloaded: {title}")
                        print(f"Duration: {duration}s, Views: {view_count:,}")
                        downloaded_count += 1

                print(f"Successfully downloaded {downloaded_count} trending videos to {INPUT_DIR}")
            else:
                print("No trending videos found")

    except Exception as e:
        error_msg = str(e)
        if "age-restricted" in error_msg.lower() or "sign in to confirm your age" in error_msg.lower():
            print("❌ Some videos are age-restricted and cannot be downloaded with current cookie setup.")
            print("To fix this:")
            print("1. Make sure you're logged into YouTube in your browser")
            print("2. Or export YouTube cookies manually: https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies")
            print("3. Save cookies as cookies/cookies.txt")
            print("4. Run: python app/main.py --check-cookies")
            print(f"Original error: {error_msg}")
        else:
            print(f"Error downloading trending videos: {e}")

def download_video_from_url(url):
    """
    Download a video from a specific YouTube URL.

    Args:
        url (str): The YouTube video URL to download
    """
    # Ensure input directory exists
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(COOKIES_DIR, exist_ok=True)

    # yt-dlp options
    ydl_opts = {
        'format': 'best',  # Get best available quality
        'outtmpl': os.path.join(INPUT_DIR, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': False,
        'no_warnings': False,
        'postprocessors': [{
            'key': 'FFmpegVideoRemuxer',
            'preferedformat': 'mp4',
        }],
    }

    # Add cookie options for age-restricted content
    cookie_opts = get_cookie_options()
    ydl_opts.update(cookie_opts)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading video from: {url}")
            info_dict = ydl.extract_info(url, download=True)
            
            if info_dict:
                title = sanitize_filename(info_dict.get('title', 'Unknown'))
                duration = info_dict.get('duration', 0)
                view_count = info_dict.get('view_count', 0)
                
                # Check if file was downloaded to current directory and move it
                expected_filename = f"{title}.{info_dict.get('ext', 'mp4')}"
                current_dir_file = os.path.join(os.getcwd(), expected_filename)
                target_file = os.path.join(INPUT_DIR, expected_filename)
                
                if os.path.exists(current_dir_file) and not os.path.exists(target_file):
                    print(f"Moving downloaded file to {INPUT_DIR}")
                    os.rename(current_dir_file, target_file)
                
                print(f"Downloaded: {title}")
                print(f"Duration: {duration}s, Views: {view_count:,}")
                print(f"Successfully downloaded video to {INPUT_DIR}")
            else:
                print("Failed to download video")

    except Exception as e:
        error_msg = str(e)
        if "age-restricted" in error_msg.lower() or "sign in to confirm your age" in error_msg.lower():
            print("❌ Video is age-restricted and cannot be downloaded with current cookie setup.")
            print("To fix this:")
            print("1. Make sure you're logged into YouTube in your browser")
            print("2. Or export YouTube cookies manually: https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies")
            print("3. Save cookies as cookies/cookies.txt")
            print("4. Run: python app/main.py --check-cookies")
            print(f"Original error: {error_msg}")
        else:
            print(f"Error downloading video: {e}")

if __name__ == "__main__":
    # Example usage
    topic = input("Enter a topic to search for popular videos: ")
    download_popular_videos(topic)