import pytest
import asyncio
from wolflive.client import WolfClient

@pytest.mark.asyncio
async def test_connect_and_close_monkeypatch(monkeypatch):
    called = {}

    class DummyWS:
        async def close(self): pass
        def __aiter__(self):
            return iter([])

    async def fake_ws_connect(self, url, headers=None):
        called['url'] = url
        return DummyWS()

    class DummySession:
        async def ws_connect(self, url, headers=None):
            return await fake_ws_connect(self, url, headers)
        async def close(self): pass
        async def post(self, *args, **kwargs):
            class R:
                status = 200
                async def json(self): return {"token":"abc"}
                async def text(self): return ""
                async def __aenter__(self): return self
                async def __aexit__(self, *a): pass
            return R()

    monkeypatch.setattr('aiohttp.ClientSession', lambda *a, **k: DummySession())
    client = WolfClient(base_url="https://example", ws_url="wss://example/ws")
    await client.connect(token="t1")
    assert called.get('url') == "wss://example/ws"
    await client.close()
