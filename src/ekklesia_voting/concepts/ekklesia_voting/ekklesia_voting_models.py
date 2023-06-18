class Index:
    pass


class Login:
    def __init__(
        self,
        request=None,
        username=None,
        back_url=None,
        from_redirect=None,
    ):
        self.request = request
        self.username = username
        self.back_url = back_url
        self.from_redirect = from_redirect
        self.user = None


class Logout:
    pass
