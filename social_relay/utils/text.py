import bleach


def safe_text(text):
    """Clean text, stripping all tags, attributes and styles."""
    return bleach.clean(text, tags=[], attributes=[], styles=[], strip=True)
