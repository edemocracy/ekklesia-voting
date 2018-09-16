from ekklesia_voting.app import App
from .ekklesia_voting_cells import IndexCell


@App.path(path='')
class Index:
    pass


@App.html(model=Index)
def index(self, request):
    return IndexCell(self, request).show()
