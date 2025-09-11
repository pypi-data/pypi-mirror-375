import asyncio
from typing import Callable, Dict, Any, Optional
import aiohttp
from .utils import to_json, ensure_event_callable
from .exceptions import ConnectionError, AuthError, SendError

class WolfClient:
    """Async Wolf client.

    Async-first using aiohttp for HTTP and websockets, with compatibility aliases to ease porting.
    """

    def __init__(self, base_url: str = "https://api.wolf.live", ws_url: str = "wss://ws.wolf.live") -> None:
        self.base_url = base_url.rstrip("/")
        self.ws_url = ws_url
        self._session: Optional[aiohttp.ClientSession] = None
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._events: Dict[str, Callable[[Any], Any]] = {}
        self._recv_task: Optional[asyncio.Task] = None
        self._closed = True

    @classmethod
    def Client(cls, *args, **kwargs):
        """Alias for constructor (mimics TS named export)."""
        return cls(*args, **kwargs)

    async def _ensure_session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession()

    async def connect(self, token: Optional[str] = None) -> None:
        """Open websocket connection with optional auth token."""
        await self._ensure_session()
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        try:
            self._ws = await self._session.ws_connect(self.ws_url, headers=headers)
        except Exception as e:
            raise ConnectionError(f"failed to connect to {self.ws_url}: {e}") from e
        self._closed = False
        self._recv_task = asyncio.create_task(self._receiver_loop())

    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate via HTTP login; returns auth info dict."""
        await self._ensure_session()
        payload = {"username": username, "password": password}
        try:
            async with self._session.post(f"{self.base_url}/auth/login", json=payload) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise AuthError(f"login failed: {resp.status} {text}")
                return await resp.json()
        except AuthError:
            raise
        except Exception as e:
            raise ConnectionError(f"login request failed: {e}") from e

    async def send_message(self, channel: str, message: str) -> None:
        """Send a message over websocket."""
        if self._ws is None:
            raise SendError("websocket not connected")
        payload = {"type": "message", "channel": channel, "text": message}
        await self._ws.send_str(to_json(payload))

    async def sendMessage(self, channel: str, message: str) -> None:
        """Alias for send_message (compatibility)."""
        return await self.send_message(channel, message)

    def on(self, event_name: str, callback: Callable[[Any], Any]) -> None:
        """Register an event handler (sync or async function)."""
        ensure_event_callable(callback)
        self._events[event_name] = callback

    async def _receiver_loop(self):
        assert self._ws is not None
        try:
            async for msg in self._ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = msg.json()
                    except Exception:
                        data = msg.data
                    await self._dispatch_event(data)
                elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                    break
        except Exception:
            pass
        finally:
            self._closed = True

    async def _dispatch_event(self, data):
        event = data.get("event") if isinstance(data, dict) else None
        handler = self._events.get(event or "message")
        if handler:
            if asyncio.iscoroutinefunction(handler):
                await handler(data)
            else:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, handler, data)

    async def close(self):
        """Gracefully close WS and HTTP session."""
        if self._recv_task:
            self._recv_task.cancel()
            try:
                await self._recv_task
            except Exception:
                pass
        if self._ws:
            await self._ws.close()
            self._ws = None
        if self._session:
            await self._session.close()
            self._session = None
        self._closed = True

    def run(self):
        """Synchronous facade for quick scripts: manages event loop internally."""
        return _SyncFacade(self)

class _SyncFacade:
    def __init__(self, client: WolfClient):
        self._client = client
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            self._loop.run_until_complete(self._client.close())
        finally:
            self._loop.close()

    def sendMessage(self, channel: str, message: str):
        """Sync wrapper for sendMessage."""
        return self._loop.run_until_complete(self._client.sendMessage(channel, message))
