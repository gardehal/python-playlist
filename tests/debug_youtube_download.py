import yt_dlp
from infrastructure.providers.youtube_provider import YoutubeProvider

def test_download():
    provider = YoutubeProvider()
    # A known working YouTube audio URL (short duration)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 
    try:
        print(f"Attempting to download stream from: {test_url}")
        content = provider.download_stream(test_url)
        if content and len(content) > 0:
            print("Success! Downloaded bytes:", len(content))
        else:
            print("Download succeeded but returned empty content.")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_download()
