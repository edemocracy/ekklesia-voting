from urllib.parse import quote

from ekklesia_common.cell import Cell
from ekklesia_common.ekklesia_auth import EkklesiaAuthPathApp, EkklesiaLogin

from .ekklesia_voting_models import Index, Login, Logout
from ekklesia_voting.app import App

from markupsafe import Markup
from ekklesia_common.debug.tbtools import Traceback

from ..ballot.ballots import Ballots


class LayoutCell(Cell):
    def language(self):
        return self._request.i18n.get_locale().language

    def change_language_action(self):
        return self.link(Index(), name="change_language")

    def flashed_messages(self):
        try:
            return self._request.browser_session.pop("flashed_messages")
        except KeyError:
            return []

    def settings_languages(self):
        return self._app.settings.app.languages

    def favicon_url(self):
        return self.static_url("favicon.ico")

    def page_url(self):
        return self._request.url

    def brand_title(self):
        return self._s.app.title

    def show_login_button(self):
        return self._s.app.login_visible

    def login_url(self):
        if self._request.path_qs != "/":
            back_url = self._request.path_qs
        else:
            back_url = None

        return self.link(Login(back_url=back_url))

    def ballots_url(self):
        return self.link(Ballots())

    def logout_action(self):
        return self.link(Logout())

    def custom_footer_url(self):
        return self._s.app.custom_footer_url

    def tos_url(self):
        return self._s.app.tos_url

    def data_protection_url(self):
        return self._s.app.data_protection_url

    def faq_url(self):
        return self._s.app.faq_url

    def imprint_url(self):
        return self._s.app.imprint_url

    def source_code_url(self):
        return self._s.app.source_code_url


class ExceptionCell(LayoutCell):

    model_properties = ["task_uuid", "xid"]

    @property
    def insecure_development_mode_enabled(self):
        return self._s.app.insecure_development_mode

    def show_exception_details(self):
        return self.insecure_development_mode_enabled

    def traceback(self):
        if self.insecure_development_mode_enabled:
            exc = self._model.__cause__
            werkzeug_traceback = Traceback(exc.__class__, exc, exc.__traceback__)
            return Markup(werkzeug_traceback.render_full())


@App.cell(Index)
class IndexCell(LayoutCell):
    def insecure_development_mode_enabled(self):
        return self._app.settings.app.insecure_development_mode


@App.cell(Login)
class LoginCell(LayoutCell):
    model_properties = ["username", "back_url", "from_redirect"]

    def ekklesia_login_url(self):
        ekklesia_app = self._app.child(EkklesiaAuthPathApp)
        return self.link(EkklesiaLogin(back_url=self._model.back_url), app=ekklesia_app)

    def ekklesia_login_name(self):
        return self._s.ekklesia_auth.display_name

    def insecure_development_mode_enabled(self):
        return self._s.app.insecure_development_mode

    def show_internal_login(self):
        return self.insecure_development_mode_enabled or self._model.internal_login

    def show_ekklesia_login(self):
        return self._s.ekklesia_auth.enabled

    def back_url_quoted(self):
        if self._model.back_url:
            return quote(self._model.back_url)
        else:
            return None
