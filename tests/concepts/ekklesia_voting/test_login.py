from ekklesia_common.testing import get_session
from ekklesia_voting.datamodel import Voter


def test_show_dev_login(app, client):
    app.settings.app.insecure_development_mode = True
    res = client.get("/login")
    assert "AUID" in res


def test_submit_dev_login_logout(app, client, voter: Voter):
    app.settings.app.insecure_development_mode = True
    res = client.post("/login", dict(auid=voter.auid), status=302)
    session = get_session(app, client)
    assert "user_id" in session

    client.post("/logout", status=302)
    assert "session" not in client.cookies
