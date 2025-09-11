import pytest, httpx
from phrappy import Phrappy, AsyncPhrappy

def test_sync_context_manager_and_user_agent(monkeypatch):
    seen = {}
    def fake_request(self, method, url, headers=None, **kw):
        seen["method"], seen["url"], seen["headers"] = method, url, headers or {}
        return httpx.Response(200, json={"ok": True}, request=httpx.Request(method, url))
    monkeypatch.setattr(httpx.Client, "request", fake_request)

    with Phrappy(token="ApiToken abc", base_url="https://example.test") as c:
        r = c.make_request("GET", "/foo")
        assert r.status_code == 200
    assert getattr(c, "_client").is_closed is True
    assert "User-Agent" in seen["headers"] and "phrappy/" in seen["headers"]["User-Agent"]

@pytest.mark.asyncio
async def test_async_context_manager_and_user_agent(monkeypatch):
    seen = {}
    async def fake_request(self, method, url, headers=None, **kw):
        seen["method"], seen["url"], seen["headers"] = method, url, headers or {}
        return httpx.Response(200, json={"ok": True}, request=httpx.Request(method, url))
    monkeypatch.setattr(httpx.AsyncClient, "request", fake_request)

    async with AsyncPhrappy(token="ApiToken abc", base_url="https://example.test") as c:
        r = await c.make_request("GET", "/bar")
        assert r.status_code == 200
    assert getattr(c, "_client").is_closed is True
    assert "User-Agent" in seen["headers"] and "phrappy/" in seen["headers"]["User-Agent"]

def test_per_request_user_agent_override(monkeypatch):
    seen = {}
    def fake_request(self, method, url, headers=None, **kw):
        seen["headers"] = headers or {}
        return httpx.Response(200, json={"ok": True}, request=httpx.Request(method, url))
    monkeypatch.setattr(httpx.Client, "request", fake_request)

    with Phrappy(token="ApiToken abc", base_url="https://example.test") as c:
        r = c.make_request("GET", "/baz", headers={"User-Agent": "my-UA/1.2"})
        assert r.status_code == 200
    assert seen["headers"].get("User-Agent") == "my-UA/1.2"
