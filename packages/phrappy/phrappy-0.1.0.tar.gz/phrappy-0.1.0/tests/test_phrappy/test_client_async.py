# tests/test_phrappy/test_client.py
import pytest

@pytest.mark.live
@pytest.mark.asyncio
async def test_who_am_i(aclient):
    me = await aclient.authentication.who_am_i()
    assert getattr(me, "user", None) and getattr(me.user, "uid", None)
    assert isinstance(aclient.token, str) and aclient.token.startswith("ApiToken ")
