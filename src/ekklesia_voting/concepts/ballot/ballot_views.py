from uuid import UUID, uuid5

import deform
from ekklesia_common.identity_policy import NoIdentity
from ekklesia_common.permission import WritePermission, ViewPermission
from eliot import start_action, log_message
from morepath import redirect

# from webob.exc import HTTPBadRequest
from ekklesia_voting.app import App
from ekklesia_voting.datamodel import Ballot, OptionResponse, VerificationToken
from .ballot_cells import (
    BallotCell,
    BallotVoteCell,
    BallotConfirmCell,
    BallotsCell,
)
from .ballot_contracts import ballot_form
from .ballots import Ballots
from datetime import datetime


class VotePermission(ViewPermission):
    pass


@App.permission_rule(model=Ballot, permission=VotePermission)
def ballot_permission(identity, model, permission):
    return True


@App.permission_rule(model=Ballots, permission=VotePermission)
def ballots_permission(identity, model, permission):
    return True


@App.path(model=Ballots, path="ballots")
def ballots():
    return Ballots()


@App.path(model=Ballot, path="ballots/{uuid}")
def ballot(request, uuid):
    return request.q(Ballot).get(uuid)


@App.html(model=Ballots, permission=VotePermission)
def index(self, request):
    cell = BallotsCell(self, request)
    return cell.show()


@App.html(model=Ballot, permission=VotePermission)
def show(self, request):
    cell = BallotCell(self, request)
    return cell.show()


@App.html(model=Ballot, name="confirm", permission=VotePermission)
def confirm(self, request):
    cell = BallotConfirmCell(self, request)
    return cell.show()


@App.html(
    model=Ballot, name="confirm", request_method="POST", permission=VotePermission
)
def confirm_post(self, request):
    voter_id = request.current_user.id
    confirmed_token = request.POST.getall("token")
    votes_to_confirm = (
        request.q(OptionResponse)
        .join(VerificationToken)
        .filter(
            VerificationToken.voter_id == voter_id,
            VerificationToken.token.in_(confirmed_token),
        )
    )

    for vote in votes_to_confirm:
        vote.confirmed_at = datetime.now()

    token_str = ",".join(confirmed_token)

    return f"Votes confirmed für Token {token_str}. Thank you!"


@App.html(model=Ballot, name="vote", permission=VotePermission)
def vote(self, request):
    cell = BallotVoteCell(self, request)
    return cell.show()


@App.html(model=Ballot, name="vote", request_method="POST", permission=VotePermission)
def vote_post(self, request):
    form = ballot_form(self, request)
    controls = list(request.POST.items())
    with start_action(
        action_type="validate_form",
        controls=dict(c for c in controls if not c[0].startswith("_")),
        form=form,
    ) as action:
        try:
            appstruct = form.validate(controls)
        except deform.ValidationFailure:
            log_message(message_type="validation-errors", errors=form.error.asdict())
            if request.app.settings.common.fail_on_form_validation_error:
                raise form.error
            return

        action.add_success_fields(appstruct=appstruct)

        for option in self.options:
            result = appstruct[str(option.uuid)]
            vote = OptionResponse(option=option)

            if "yes_no" in result:
                vote.yes_no = result["yes_no"]

            if "points" in result:
                vote.points = result["points"]

            if "rank" in result:
                vote.rank = result["rank"]

            vote_token = VerificationToken(voter=request.current_user, response=vote)
            request.db_session.add(vote_token)

    return redirect(request.link(self, "confirm"))
