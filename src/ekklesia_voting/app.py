import logging
import os

from eliot import start_task, start_action, log_call
from ekklesia_common import database
from ekklesia_common.app import EkklesiaBrowserApp
import morepath
import ekklesia_voting
from ekklesia_voting.identity_policy import EkklesiaVotingIdentityPolicy


logg = logging.getLogger(__name__)

class BaseApp(EkklesiaBrowserApp):
    package_name = 'ekklesia_voting'


class App(BaseApp):
    pass


@BaseApp.setting_section(section="database")
def database_setting_section():
    return {
        "uri": "postgresql+psycopg2://ekklesia_voting:ekklesia_voting@127.0.0.1/ekklesia_voting"
    }


@App.identity_policy()
def get_identity_policy():
    return EkklesiaVotingIdentityPolicy()


@App.verify_identity()
def verify_identity(identity):
    return True


@log_call
def get_app_settings(settings_filepath=None):
    settings = {}

    if settings_filepath is None:
        settings_filepath = os.environ.get('EKKLESIA_VOTING_CONFIG')

    if settings_filepath is None:
        logg.info("no config file given, using defaults")
    elif os.path.isfile(settings_filepath):
        with open(settings_filepath) as config:
            settings = yaml.safe_load(config)
        logg.info("loaded config from %s", settings_filepath)
    else:
        logg.warn("config file path %s doesn't exist!", settings_filepath)

    return settings


@log_call
def get_locale(request):
    locale = request.browser_session.get('lang')
    if locale:
        logg.debug('locale from session: %s', locale)
    else:
        locale = request.accept_language.best_match(['de', 'en', 'fr'])
        logg.debug('locale from request: %s', locale)

    return locale


@log_call
def make_wsgi_app(settings_filepath=None, testing=False):
    with start_action(action_type='morepath_scan'):
        morepath.autoscan()
        morepath.scan(ekklesia_voting)

    with start_action(action_type='settings'):
        settings = get_app_settings(settings_filepath)
        App.init_settings(settings)

    with start_action(action_type='make_app'):
        App.commit()
        app = App()

    database.configure_sqlalchemy(app.settings.database, testing)
    app.babel_init()
    app.babel.localeselector(get_locale)
    return app
