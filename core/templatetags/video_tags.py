import re
from django import template

register = template.Library()

@register.filter
def youtube_id(url):
    if not url:
        return ''
    for pattern in [
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'[?&]v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
    ]:
        m = re.search(pattern, url)
        if m:
            return m.group(1)
    return ''
