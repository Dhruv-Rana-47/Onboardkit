from django import template
from urllib.parse import urlparse, parse_qs

register = template.Library()

@register.filter
def video_embed_url(url):
    if not url:
        return None

    if "youtube.com/watch" in url:
        video_id = parse_qs(urlparse(url).query).get("v", [None])[0]
        return f"https://www.youtube.com/embed/{video_id}" if video_id else url

    elif "youtu.be/" in url:
        video_id = urlparse(url).path.lstrip("/")
        return f"https://www.youtube.com/embed/{video_id}"

    elif "vimeo.com" in url:
        video_id = url.split("/")[-1]
        return f"https://player.vimeo.com/video/{video_id}"

    elif url.lower().endswith((".mp4", ".webm", ".ogg")):
        return url

    return url

@register.filter
def is_direct_video(url):
    return url.lower().endswith((".mp4", ".webm", ".ogg"))
