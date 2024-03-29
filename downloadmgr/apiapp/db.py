import click
import enum
import sqlite3
from flask import g, current_app
from flask.cli import with_appcontext

DATABASE = "segments.db"
SCHEMA = "schema.sql"


class RecordStatus(enum.Enum):
    UNKNOWN = None
    DL_REQUESTED = "sent-to-worker"
    DL_STARTED = "started"
    DL_FAILED = "failed"
    DL_MISSING = "missing"
    DL_COMPLETED = "completed"

    @staticmethod
    def values():
        return {
            RecordStatus.UNKNOWN.value,
            RecordStatus.DL_REQUESTED.value,
            RecordStatus.DL_STARTED.value,
            RecordStatus.DL_FAILED.value,
            RecordStatus.DL_MISSING.value,
            RecordStatus.DL_COMPLETED.value
        }


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource(SCHEMA) as f:
        db.executescript(f.read().decode('utf8'))


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


@click.command("ingest-raw")
@click.argument("data-csv", type=click.Path(exists=True))
@with_appcontext
def ingest_raw_data(data_csv):
    click.secho(f"Loading data from {data_csv}")

    import pandas as pd

    df = pd.read_csv(data_csv, compression="zip", index_col=0)
    df.loc[:, "state"] = RecordStatus.UNKNOWN.value
    df = df.rename(columns={"YTID": "ytid"})
    click.echo(f"n segments: {len(df)}")

    click.echo(f"A random sampling:")
    click.echo(f"{df.sample(3)}")

    db = get_db()
    df.to_sql("segments", db, index_label="id", method="multi",
              if_exists="replace", chunksize=32)

    click.echo("Checking number of rows...")
    cursor = db.execute("SELECT COUNT(*) from segments")
    for row in cursor:
        for member in row:
            print(member)


@click.command("bulk-update-state")
@click.argument("text-file", type=click.Path(exists=True))
@click.argument("state", type=click.Choice(RecordStatus.values()))
@with_appcontext
def bulk_update_state(text_file, state):
    """Update many IDs at once using a text file.
    
    The text file should contain one YTID per line.
    If it is a CSV, it will look at the first element in the line only,
    stopping at the first comma.
    """
    ytids = []
    with open(text_file, "r") as fh:
        for line in fh:
            first_comma = line.find(",")
            if first_comma != -1:
                line = line[:first_comma]
            ytids.append(line.strip())

    db = get_db()

    for ytid in ytids:
        query = (
                f'UPDATE segments SET state = "{state}"'
                f' WHERE ytid = "{ytid}"'
            )
        db.execute(query)
    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(ingest_raw_data)
    app.cli.add_command(bulk_update_state)
