from ekklesia_voting.datamodel import BallotVoting


class BallotVotings:
    def ballot_votings(self, q):
        query = q(BallotVoting)
        return query.all()
