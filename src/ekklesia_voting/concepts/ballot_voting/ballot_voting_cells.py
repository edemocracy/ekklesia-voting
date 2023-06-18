from ekklesia_voting.app import App
from ekklesia_voting.datamodel import BallotVoting
from .ballot_voting_contracts import ballot_voting_form
from .ballot_votings import BallotVotings
from ..ekklesia_voting.ekklesia_voting_cells import LayoutCell


@App.cell(BallotVotings)
class BallotVotingsCell(LayoutCell):
    def ballot_votings(self):
        return list(self._model.ballot_votings(self._request.q))


@App.cell(BallotVoting)
class BallotVotingCell(LayoutCell):
    model_properties = ["ends_at", "starts_at", "title"]

    def vote_url(self):
        return self.link(self._model, "vote")


@App.cell(BallotVoting, "vote")
class BallotVotingVoteCell(LayoutCell):
    model_properties = ["ends_at", "starts_at", "title", "description"]

    def form_html(self):
        form = ballot_voting_form(self._model, self._request)
        form_html = form.render()
        return self.markup_class(form_html)


@App.cell(BallotVoting, "confirm")
class BallotVotingConfirmCell(LayoutCell):
    model_properties = ["title"]
    _model: BallotVoting

    def confirm_action(self):
        return self.link(self._model, "confirm")

    def voting_type(self):
        voting = self._model

        if voting.use_rank:
            return "stv"

        if voting.use_yes_no and voting.max_points:
            return "scored"

        if voting.use_yes_no:
            return "yes_no"

        if voting.max_points:
            return "candidate_list"

    def votes_to_confirm(self):
        def ee(token, vote, option):

            vote = {
                "token": token,
                "title": option.title,
                "points": vote.points,
                "rank": vote.rank,
                "yes_no": vote.yes_no,
            }

            return vote

        auid = self._request.browser_session["auid"]
        votes = [ee(*t) for t in self._model.votes_to_confirm(auid)]

        voting = self._model

        if voting.use_rank:
            return sorted(votes, key=lambda v: v["rank"] or 999)

        if voting.max_points:
            return sorted(votes, key=lambda v: v["points"] or 0, reverse=True)

        if voting.use_yes_no:
            return sorted(votes, key=lambda v: v["yes_no"] or False)

        return votes
