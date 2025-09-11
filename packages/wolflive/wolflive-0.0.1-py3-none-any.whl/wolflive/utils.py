import json

def to_json(obj):
    """Convert object to compact JSON string."""
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)

def ensure_event_callable(cb):
    """Ensure that event handler is callable, else raise TypeError."""
    if not callable(cb):
        raise TypeError("event handler must be callable")
    return cb
