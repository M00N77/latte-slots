import uuid

JITSI_BASE = "https://meet.jit.si"


def _slug(title):
    safe = "".join(c if (c.isascii() and c.isalnum()) or c in "-_ " else "_" for c in title).strip()
    return (safe.replace(" ", "_")[:30]) or "meeting"


def create_jitsi_room(title):
    room = f"{_slug(title)}-{uuid.uuid4().hex[:8]}"
    return f"{JITSI_BASE}/{room}"


def create_meeting_room(title):
    return create_jitsi_room(title)
