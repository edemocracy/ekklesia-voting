from datetime import datetime
from pathlib import Path
from typing import Optional

import mimesis
import sqlalchemy.orm
import transaction
import typer
from alembic import command
from alembic.config import Config
from sqlalchemy import pool
from typer import Option, confirm, Exit

import ekklesia_common.logging


def main(
    config_file: Optional[Path] = Option(
        None,
        "--config-file",
        "-c",
        help=(
            "Path to config file in YAML / JSON format. Default: Built-in test config "
            "(DB test_ekklesia_voting)"
        ),
        readable=True,
    ),
    doit: bool = Option(
        False, "--doit", help="Don't ask, just drop and recreate the database"
    ),
    log_path: Path = Option(
        Path("."),
        help="Directory where to write logs to.",
        file_okay=False,
        writable=True,
    ),
):
    """
    Create an ekklesia-voting database for testing.
    This is needed for running pytest.
    """

    log_file = log_path / "create_test_db.log.json"
    print(f"Log output goes to {log_file}")

    ekklesia_common.logging.init_logging(open(log_file, "w"))

    from ekklesia_voting.app import make_wsgi_app, App
    from fixtures import get_test_settings, get_db_uri

    if config_file:
        app = make_wsgi_app(config_file)
    else:
        settings = get_test_settings(get_db_uri())
        App.init_settings(settings)
        app = make_wsgi_app(testing=True)

    from ekklesia_common.database import db_metadata, Session

    # local import because we have to set up the database stuff before that

    print(f"using config file {config_file}")
    print(f"using db url {app.settings.database.uri}")

    engine = sqlalchemy.create_engine(
        app.settings.database.uri, poolclass=pool.NullPool
    )
    connection = engine.connect()
    connection.execute("select")

    sqlalchemy.orm.configure_mappers()

    if doit:
        confirmed = True
    else:
        print(80 * "=")
        confirmed = confirm("Drop and recreate the database now?", default=False)

    if not confirmed:
        print("Not confirmed, doing nothing.")
        raise Exit(3)

    db_metadata.drop_all()
    connection.execute("DROP TABLE IF EXISTS alembic_version")
    db_metadata.create_all()

    transaction.commit()

    print("Committed database changes.")

    alembic_cfg = Config("./alembic.ini")
    alembic_cfg.attributes["connection"] = connection

    command.stamp(alembic_cfg, "head")

    # Fixes a strange error message when the connection isn't closed.
    # Didn't happen before.
    connection.close()
    print("Finished successfully.")


if __name__ == "__main__":
    typer.run(main)
