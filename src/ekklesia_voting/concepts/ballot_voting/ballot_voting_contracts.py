from colander import SchemaNode, Mapping, Int, Boolean, OneOf
from deform import Button
from deform.widget import RadioChoiceWidget
from ekklesia_common.contract import Schema, Form
from ekklesia_common.translation import _

from ekklesia_voting.datamodel import BallotVoting


def ballot_voting_form(ballot_voting: BallotVoting, request):
    yes_no_choices = [(True, _("Yes")), (False, _("No")), (None, _("Abstention"))]

    if ballot_voting.max_points:
        point_choices = [
            (i, str(i))
            for i in range(ballot_voting.min_points, ballot_voting.max_points + 1)
        ]
    else:
        point_choices = None

    schema = Schema()

    rank_choices = [(i, str(i)) for i in range(1, len(ballot_voting.options) + 1)]

    for option in ballot_voting.options:

        option_schema = SchemaNode(Mapping(), name=str(option.uuid), title=option.title)

        if ballot_voting.use_yes_no:
            option_schema.add(
                SchemaNode(
                    Boolean(),
                    validator=OneOf([x[0] for x in yes_no_choices]),
                    widget=RadioChoiceWidget(values=yes_no_choices, inline=True),
                    name="yes_no",
                    title=f"Do you approve of this option?",
                )
            )

        if point_choices:
            option_schema.add(
                SchemaNode(
                    Int(),
                    validator=OneOf([x[0] for x in point_choices]),
                    widget=RadioChoiceWidget(
                        values=point_choices, inline=True, null_value="0"
                    ),
                    name="points",
                    title="How do you rate this option? 0 is the lowest value. Higher is better.",
                    missing=0,
                )
            )

        if ballot_voting.use_rank:
            option_schema.add(
                SchemaNode(
                    Int(),
                    validator=OneOf([x[0] for x in rank_choices]),
                    widget=RadioChoiceWidget(
                        values=rank_choices, inline=True, null_value="0"
                    ),
                    name="rank",
                    title="Which rank do you assign to this option? 1 is the best. Leave empty to abstain.",
                    missing=0,
                )
            )

        schema.add(option_schema)

    form = Form(schema, request, buttons=[Button(title=_("button_check_vote"))])
    return form


def validate_form(form):
    pass
