from ekklesia_voting.datamodel import Ballot


class Ballots:
    def ballots(self, q):
        query = q(Ballot)
        return query.all()
