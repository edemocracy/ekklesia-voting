from ekklesia_portal.helper.cell import JinjaCellEnvironment
from ekklesia_portal.helper.concept import ConceptApp
from ekklesia_portal.helper.templating import make_jinja_env, make_template_loader
from ekklesia_voting.request import EkklesiaVotingRequest
import ekklesia_voting
import morepath


class App(ConceptApp):

    request_class = EkklesiaVotingRequest

    def __init__(self):
        super().__init__()
        self.jinja_env = make_jinja_env(jinja_environment_class=JinjaCellEnvironment,
                                        jinja_options=dict(loader=make_template_loader(App.config, 'ekklesia_voting')),
                                        app=self)


def make_wsgi_app():
    morepath.autoscan()
    App.commit()
    app = App()
    return app
