from urllib.parse import urlparse, unquote

import morepath
from eliot import log_message
from morepath import redirect
from webob.exc import HTTPBadRequest

from ekklesia_voting.app import App
from .ekklesia_voting_cells import ExceptionCell, IndexCell, LoginCell
from .ekklesia_voting_models import Index, Login, Logout

from ekklesia_common.app import UnhandledRequestException
from ...datamodel import Voter


def unquote_or_none(url):
    if url is None:
        return url
    else:
        return unquote(url)


# Paths

App.path(path="")(Index)


@App.path(model=Login, path="/login")
def login(request, back_url=None, from_redirect=False):

    return Login(
        back_url=unquote_or_none(back_url),
        from_redirect=from_redirect,
    )


App.path(path="/logout")(Logout)


# Views


@App.html(model=Index)
def index(self, request):
    return IndexCell(self, request).show()


@App.html(model=UnhandledRequestException)
def exception(self, request):
    return ExceptionCell(self, request).show()


@App.html(model=Index, name="change_language", request_method="POST")
def change_language(self, request):
    lang = request.POST.get("lang")
    if lang not in request.app.settings.app.languages:
        raise HTTPBadRequest("unsupported language")

    back_url = request.POST.get("back_url")
    parsed_app_url = urlparse(request.application_url)
    parsed_back_url = urlparse(back_url)

    if parsed_app_url.netloc != parsed_back_url.netloc:
        log_message(message_type="invalid_redirect", url=back_url)
        raise HTTPBadRequest("redirect not allowed")

    request.browser_session["lang"] = lang
    return redirect(back_url)


@App.html(model=Login)
def show_login(self, request):
    return LoginCell(self, request).show()


@App.html(model=Login, request_method="POST")
def dev_login_post(self, request):
    if not request.app.settings.app.insecure_development_mode:
        raise HTTPBadRequest()

    @request.after
    def remember(response):
        auid = request.POST.get("auid")
        test_voter = request.q(Voter).filter_by(auid=auid).one()
        identity = morepath.Identity(test_voter.id, user=test_voter)
        request.app.root.remember_identity(response, request, identity)

    return redirect("/")


@App.html(model=Logout, request_method="POST")
def logout(self, request):
    @request.after
    def forget(response):
        request.app.forget_identity(response, request)

    index_url = request.link(Index())

    if request.app.settings.app.insecure_development_mode:
        return redirect(index_url)

    # Redirect to the logout endpoint of the OIDC provider which then redirects back
    # to our index page.
    return redirect(request.ekklesia_auth.logout_url(index_url))
