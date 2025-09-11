class WolfError(Exception):
    """Base class for wolflive errors."""

class ConnectionError(WolfError):
    """Connection-level problems (HTTP or WS)."""
    pass

class AuthError(WolfError):
    """Authentication failure."""
    pass

class SendError(WolfError):
    """Failure during sending a message."""
    pass
