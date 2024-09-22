import re


def youtube_id_from_url(url: str) -> str:
    """Youtube ID from URL
    Extract the Youtube video ID from a URL.
    """
    youtube_regex = r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})"
    youtube_id = re.match(youtube_regex, url)
    if youtube_id:
        return youtube_id.group(1)
    else:
        raise Exception("Invalid Youtube URL")