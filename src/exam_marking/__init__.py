import csv
import re
from itertools import batched
from pathlib import Path
from typing import IO, Optional

import click
from flask import Flask, g

from exam_marking import routes

ZID_REGEX = re.compile(r"z[0-9]{7,8}")
SEPARATOR_REGEX = re.compile(
    r"####################\n##### (z[0-9]{7}) #####\n####################"
)


def strip_lines(a: str):
    while (b := a.strip("\n -_")) != a:
        a = b
    return a


@click.command(
    help="Reads answers and marks from MARKS_PATH and starts a webserver where you can fill in marks. Marks will be saved periodically and when you Ctrl+C the process."
)
@click.option(
    "--import-answers",
    type=click.File(),
    help="Imports answers from the provided txt file. Overwrites file at MARKS_PATH. Answers are expected to be separated by a block of hashes 20 wide, with the center of the middle line containing a zID (z[0-9]{7}) with a single space on either side.",
)
@click.option(
    "--column",
    "columns",
    type=(str, bool, int),
    multiple=True,
    help="A set of columns to provide in the marking interface. Each column should have a name, either true or false to indicate whether it is a checkbox or not, and a maximum value (or the value for true checkboxes).",
)
@click.option("--port", type=int, help="Port to use for webserver. Defaults to 8000.")
@click.argument(
    "marks_path",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
)
def main(
    import_answers: Optional[IO[str]],
    columns: list[str],
    marks_path: Path,
    port: Optional[int],
) -> None:
    app = Flask(__name__)

    seen_zids = set()
    MARKS = []
    max_extra_cols = 0
    if import_answers:
        if marks_path.exists() and not click.confirm(
            "That marks file already exists, are you sure you want to overwrite it?"
        ):
            raise click.ClickException("Aborting to not overwrite existing marks.")

        answers = SEPARATOR_REGEX.split(import_answers.read())
        answers = [strip_lines(a) for a in answers if strip_lines(a)]

        for i in range(0, len(answers), 2):
            zid, answer = answers[i : i + 2]
            assert ZID_REGEX.match(zid) and not ZID_REGEX.match(
                answer
            ), f"an answer assigned to '{zid}' is invalid"
            MARKS.append(
                {
                    "zid": zid,
                    "answer": answer,
                    "symp": 0,
                    "marks": [None for _ in columns],
                }
            )
            if zid in seen_zids:
                raise click.ClickException(f"Error: '{zid}' is seen twice.")
            seen_zids.add(zid)
        print(f"Imported {len(MARKS)} answers!")
    else:
        with open(marks_path, "r") as f:
            cf = csv.DictReader(f, fieldnames=["zid", "answer"], restkey="marks")

            for row in cf:
                MARKS.append(
                    {
                        **row,
                        "marks": [None if m == "" else m for m in row["marks"]],
                    }
                )
                if len(row["marks"]) > len(columns):
                    max_extra_cols = len(columns) - len(row["marks"])
                if row["zid"] in seen_zids:
                    raise click.ClickException(f"Error: '{row['zid']}' is seen twice.")
                seen_zids.add(row["zid"])
        print(f"Opened {len(MARKS)} rows!")

    def save():
        with open(marks_path, "w") as f:
            cf = csv.writer(f)

            for row in MARKS:
                cf.writerow(
                    [
                        row["zid"],
                        row["answer"],
                        *["" if m is None else str(m) for m in row["marks"]],
                    ]
                )
        print(f"Saved changes!")

    @app.before_request
    def before_request():
        g.marks = MARKS
        g.columns = columns
        g.csv_filename = marks_path.name
        g.extra_cols = max_extra_cols
        g.save = save

    app.register_blueprint(routes.bp)

    app.run(port=port or 8000)

    save()


if __name__ == "__main__":
    main()
