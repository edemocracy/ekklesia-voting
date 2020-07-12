if __name__ == "__main__":
    from transaction import commit
    from munch import Munch
    from ekklesia_voting.app import make_wsgi_app

    app = make_wsgi_app("config.yml")
    from ekklesia_common import database
    from ekklesia_voting.app import App
    from ekklesia_voting.datamodel import *

    from tests.factories import *

    s = database.Session()
    q = s.query

    ip = get_ipython()  # type: ignore

    ip.magic("autocall 2")
