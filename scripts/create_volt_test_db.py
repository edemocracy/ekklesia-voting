import argparse
import logging
import textwrap
from datetime import datetime
from typing import NamedTuple, Optional

import sqlalchemy.orm
import transaction
from alembic import command
from alembic.config import Config
from ekklesia_common.ekklesia_auth import OAuthToken
from sqlalchemy import pool

from ekklesia_voting.app import make_wsgi_app


logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser("Ekklesia Voting create_volt_test_db.py")
parser.add_argument(
    "-c",
    "--config-file",
    help=f"Optional path to config file in YAML / JSON format. Uses default test configuration when not set.",
)
parser.add_argument("--doit", action="store_true", default=False)

if __name__ == "__main__":

    logg = logging.getLogger(__name__)

    args = parser.parse_args()

    if args.config_file:
        app = make_wsgi_app(args.config_file)
    else:
        raise RuntimeError("config file must be given!")

    from ekklesia_common.database import db_metadata, Session

    # local import because we have to set up the database stuff before that
    from ekklesia_voting.datamodel import (
        User,
        BallotOption,
        BallotVoting,
    )

    print(f"using config file {args.config_file}")
    print(f"using db url {app.settings.database.uri}")

    engine = sqlalchemy.create_engine(
        app.settings.database.uri, poolclass=pool.NullPool
    )
    connection = engine.connect()
    connection.execute("select")

    sqlalchemy.orm.configure_mappers()

    if not args.doit:
        print(80 * "=")
        input("press Enter to drop and create the database...")

    db_metadata.drop_all()
    connection.execute("DROP TABLE IF EXISTS alembic_version")
    db_metadata.create_all()

    s = Session()

    nl_user = User(
        oauth_token=OAuthToken(provider="ekklesia", token={}),
    )

    de_user = User(
        oauth_token=OAuthToken(provider="ekklesia", token={}),
    )

    class Proposition(NamedTuple):
        title: str
        content: str
        motivation: str
        voting_identifier: str
        external_discussion_url: str = ""

    q1 = Proposition(
        title="Smart State vision: small fixes",
        content=textwrap.dedent(
            """
            European citizens and residents expect their governments and public
            institutions to provide efficient and effective, high-quality public services
            as well as transparent public administrations. Europe, over decades of
            integration, has set a standard of quality in public provision, allowing for
            an unprecedented high quality of life for citizens and a unique European
            social model.

            However, in the wake of the economic crisis, growing inequality, and emerging
            technologies, trust in public institutions has disintegrated, while endemic
            corruption and inefficiency continue to plague public life.

            For Volt, public service is first and foremost intended to serve citizens and
            residents. We hold as core tenets the principles of management by objectives,
            transparency, accountability, citizen empowerment, and subsidiarity in the
            allocation of competencies.

            Volt will work to ensure that, across the European Union, public institutions
            in the Member States are reformed into a modern, forward-looking community
            with state-of-the-art technology and new thinking to tackle the preceding
            years of crisis and periods of economic recession, and in some cases, decades
            of neglect.

            In times of transformation, governments must adapt to enable every citizen to
            fully participate in and contribute to society, and provide for maximal
            social inclusion and mobility. Digital services should be used when
            digitisation improves analogue services. Smart States must adopt new tools to
            earn their citizens' trust through accountable, transparent, and efficient
            governance. Volt will invest in our common future, including not only
            innovative public services to cut waste, but also innovative education
            systems, quality healthcare, and an effective investigative and judicial
            system to combat corruption.
        """
        ),
        voting_identifier="EPT1",
        motivation="Makes some small changes to the Smart state vision",
        external_discussion_url="http://example.com",
    )

    q1_counter = Proposition(
        title="Smart State vision: keep it simple",
        content="Volt wants a Smart State, short and simple!",
        motivation="People don't want to read anymore, we need to avoid text!",
        voting_identifier="EPT2",
    )

    q1_counter_2 = Proposition(
        title="Smart State vision: random",
        content=textwrap.dedent(
            """
            Ports are created with the built-in function open_port. She spent
            her earliest years reading classic literature, and writing
            poetry. Erlang is a general-purpose, concurrent, functional
            programming language. Erlang is known for its designs that are
            well suited for systems. Ports are created with the built-in
            function open_port. Make me a sandwich. Erlang is a
            general-purpose, concurrent, functional programming language.
            Haskell is a standardized, general-purpose purely functional
            programming language, with non-strict semantics and strong static
            typing. Type classes first appeared in the Haskell programming
            language. The arguments can be primitive data types or compound
            data types. They are written as strings of consecutive
            alphanumeric characters, the first character being lowercase.
            Type classes first appeared in the Haskell programming language.
            The Galactic Empire is nearing completion of the Death Star, a
            space station with the power to destroy entire planets. Ports are
            used to communicate with the external world. Ports are used to
            communicate with the external world. Atoms are used within a
            program to denote distinguished values.
        """
        ),
        motivation=textwrap.dedent(
            """
            Just some random garbage which is completely different from the
            original test for testing.
        """
        ),
        voting_identifier="EPT3",
    )

    vote_starts_at = datetime.fromisoformat("2023-05-24")
    vote_ends_at = datetime.fromisoformat("2023-07-29")

    ballot_voting = BallotVoting(
        title="Changes to the Smart state vision",
        starts_at=vote_starts_at,
        ends_at=vote_ends_at,
        max_points=3,
        department="Volt Europa",
        description=textwrap.dedent(
            """
          This ballot consists of 3 proposal and only one can win.

          Voting system:

          * If no proposal gets more yes than no votes, all propositions are rejected.
          * Rank: The proposal with the highest sum of points is accepted.
        """
        ),
    )

    def option_from_proposition(proposition):
        title = f"{proposition.voting_identifier}: {proposition.title}"
        text = "\n\n".join(
            [
                "## Content",
                proposition.content,
                "## Motivation",
                proposition.motivation or "",
            ]
        )
        return BallotOption(title=title, text=text)

    ballot_voting.options = [
        option_from_proposition(p) for p in [q1, q1_counter, q1_counter_2]
    ]

    s.add(ballot_voting)

    def option_from_candidate_name(name):
        return BallotOption(title=name, text="More info about the candidate")

    candidates = ["X candidate", "C candidate", "Z Candidate"]

    election_stv = BallotVoting(
        title="Election (STV)",
        starts_at=vote_starts_at,
        ends_at=vote_ends_at,
        department="Volt Europa",
        use_yes_no=False,
        use_rank=True,
        description=textwrap.dedent(
            """
          This ballot consists of 3 candidates and only one can win.

          Voting system: Single transferable vote.

          Choose the order of candidates.
          Only one candidate can be 1st, only one can be 2nd and so on.
        """
        ),
    )

    s.add(election_stv)

    election_stv.options = [option_from_candidate_name(name) for name in candidates]

    election_rank = BallotVoting(
        title="Election (candidate list)",
        starts_at=vote_starts_at,
        ends_at=vote_ends_at,
        department="Volt Europa",
        use_yes_no=False,
        unique_points=True,
        min_points=0,
        max_points=2,
        description=textwrap.dedent(
            """
          This ballot consists of 3 candidates and only one can win.

          Voting system: Candidate list with Borda count.

          Rate candidates by assigning points. Multiple candidates must not have
          the same rating, so at most one with 1 point, at most one with 2 points is allowed and so on.
       """
        ),
    )

    election_rank.options = [option_from_candidate_name(name) for name in candidates]
    s.add(election_rank)

    transaction.commit()

    logg.info("committed")

    alembic_cfg = Config("./alembic.ini")
    alembic_cfg.attributes["connection"] = connection

    command.stamp(alembic_cfg, "head")

    # Fixes a strange error message when the connection isn't closed.
    # Didn't happen before.
    connection.close()

    logg.info("finished")
