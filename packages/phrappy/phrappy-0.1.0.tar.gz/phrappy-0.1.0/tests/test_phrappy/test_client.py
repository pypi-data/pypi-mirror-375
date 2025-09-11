import pytest

@pytest.mark.live
def test_who_am_i(client):
    me = client.authentication.who_am_i()
    assert getattr(me, "user", None) and getattr(me.user, "uid", None)
    assert isinstance(client.token, str) and client.token.startswith("ApiToken ")
