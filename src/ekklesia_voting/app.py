from ekklesia_common.app import EkklesiaBrowserApp
import morepath
import ekklesia_voting


class BaseApp(EkklesiaBrowserApp):
    package_name = 'ekklesia_voting'


class App(BaseApp):
    pass


def make_wsgi_app():
    morepath.autoscan()
    App.commit()
    app = App()
    return app
