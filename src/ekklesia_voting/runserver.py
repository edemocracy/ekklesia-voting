import morepath


def run():
    from ekklesia_voting.app import make_wsgi_app
    app = make_wsgi_app()
    morepath.run(app)


if __name__ == "__main__":
    run()
