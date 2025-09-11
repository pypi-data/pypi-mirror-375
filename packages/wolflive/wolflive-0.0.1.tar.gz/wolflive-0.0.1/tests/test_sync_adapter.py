def test_sync_send_message_monkeypatch(monkeypatch):
    from wolflive.sync_adapter import WolfClientSync
    sent = {}

    class DummyWS:
        def __init__(self): pass
        def send(self, text):
            sent['payload'] = text
        def run_forever(self): pass

    def fake_ws_app(url, header=None, on_message=None, on_open=None, on_close=None):
        return DummyWS()

    monkeypatch.setattr('wolflive.sync_adapter.websocket.WebSocketApp', fake_ws_app)

    client = WolfClientSync(ws_url="wss://example/ws")
    client.connect(token="abc")
    client.sendMessage("room1", "hello")
    assert 'payload' in sent
