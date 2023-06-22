import pytest

from ekklesia_common.testing import (
    assert_deform,
    fill_form,
    assert_difference,
)
from ekklesia_voting.datamodel import OptionResponse


@pytest.mark.xfail(reason="implement this :)")
def test_ballot_vote(client, db_query, ballot):
    res = client.get(f"/ballots/{ballot.uuid}")
    form = assert_deform(res)
    vote = {}
    fill_form(form, vote)

    with assert_difference(db_query(OptionResponse).count, 3):
        form.submit(status=302)
