from typing import Any, Callable, Dict, Optional
import threading
import json
from .utils import to_json, ensure_event_callable
from .exceptions import ConnectionError, SendError

try:
    import requests
    import websocket
except ImportError:
    raise ImportError("sync adapter requires 'requests' and 'websocket-client' packages")

class WolfClientSync:
    """Sync adapter: uses requests & websocket-client under the hood."""

    def __init__(self, base_url: str = "https://api.wolf.live", ws_url: str = "wss://ws.wolf.live"):
        self.base_url = base_url.rstrip("/")
        self.ws_url = ws_url
        self._ws: Optional[websocket.WebSocketApp] = None
        self._thread: Optional[threading.Thread] = None
        self._events: Dict[str, Callable[[Any], Any]] = {}
        self._connected = False

    def connect(self, token: Optional[str] = None):
        headers = [f"Authorization: Bearer {token}"] if token else None

        def on_message(ws, message):
            try:
                data = json.loads(message)
            except Exception:
                data = message
            handler = self._events.get(data.get("event") if isinstance(data, dict) else "message")
            if handler:
                handler(data)

        def on_open(ws):
            self._connected = True

        def on_close(ws, *args):
            self._connected = False

        self._ws = websocket.WebSocketApp(self.ws_url, header=headers,
                                          on_message=on_message, on_open=on_open, on_close=on_close)
        self._thread = threading.Thread(target=self._ws.run_forever, daemon=True)
        self._thread.start()

    def login(self, username: str, password: str):
        """Sync HTTP login using requests."""
        import requests
        payload = {"username": username, "password": password}
        try:
            r = requests.post(f"{self.base_url}/auth/login", json=payload, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            raise ConnectionError(f"login failed: {e}") from e

    def sendMessage(self, channel: str, message: str):
        """Sync send message over websocket."""
        if not self._ws:
            raise SendError("websocket not connected")
        try:
            payload = {"type": "message", "channel": channel, "text": message}
            self._ws.send(to_json(payload))
        except Exception as e:
            raise SendError(f"send failed: {e}") from e

    def on(self, event_name: str, callback: Callable[[Any], Any]):
        """Register event handler."""
        ensure_event_callable(callback)
        self._events[event_name] = callback
