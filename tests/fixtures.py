import logging
import os
from pathlib import Path

from ekklesia_common.database import Session
from ekklesia_common.request import EkklesiaRequest
from morepath.request import BaseRequest
from munch import Munch
from pytest import fixture
from webtest import TestApp as Client

from ekklesia_voting.app import make_wsgi_app, App

ROOT_DIR = Path(__file__).absolute().parent.parent
logg = logging.getLogger(__name__)


@fixture
def fixture_by_name(request):
    return request.getfixturevalue(request.param)


def get_db_uri():
    return os.getenv(
        "EKKLESIA_VOTING_TEST_DB_URL",
        "postgresql+psycopg2:///test_ekklesia_voting?host=/tmp",
    )


def get_test_settings(db_uri):
    return {
        "database": {"uri": db_uri},
        "app": {"default_language": "en", "languages": ["en", "de"]},
        "test_section": {"test_setting": "test"},
        "common": {"instance_name": "test", "fail_on_form_validation_error": False},
        "browser_session": {"secret_key": "test", "cookie_secure": False},
        "ekklesia_auth": {
            "client_id": "client_id_test",
            "client_secret": "test_secret",
            "authorization_url": "http://id.invalid/openid-connect/auth",
            "token_url": "http://id.invalid/openid-connect/token",
            "userinfo_url": "http://id.invalid/openid-connect/userinfo",
        },
    }


@fixture(scope="session")
def settings():
    return get_test_settings(get_db_uri())


@fixture(scope="session")
def app(settings):
    App.init_settings(settings)
    app = make_wsgi_app(testing=True)
    return app


@fixture
def client(app):
    return Client(app)


@fixture
def req(app):
    environ = BaseRequest.blank("test").environ
    req = EkklesiaRequest(environ, app)
    req.i18n = Munch(dict(gettext=(lambda s, *a, **k: s)))
    req.browser_session = {}
    return req


@fixture
def db_session(app):
    session = Session()
    yield session
    session.rollback()


@fixture
def db_query(db_session):
    return db_session.query
