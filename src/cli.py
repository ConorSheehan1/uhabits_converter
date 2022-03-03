# Standard Library
import os
from typing import List

# Third party
import fire
import inquirer
from rich.console import Console
from rich.progress import track
from rich.prompt import Prompt

from convert import Converter
from version import __version__

console = Console(color_system="auto")


def select_db() -> str:
    while True:
        proposed_db = Prompt.ask("Please choose a .db file to read from")
        if not os.path.exists(proposed_db):
            console.print(f"could not find file {proposed_db}", style="yellow")
            continue
        if not proposed_db.endswith(".db"):
            console.print(f"please choose a .db file", style="yellow")
            continue
        return proposed_db


def overwrite_file(path: str) -> bool:
    return (
        Prompt.ask(f"{path} already exists. Would you like to overwrite it?", choices=["y", "n"])
        == "y"
    )


def select_outputdb(outputdb, overwrite: bool = False) -> str:
    while True:
        if not os.path.exists(outputdb):
            return outputdb

        if overwrite or overwrite_file(outputdb):
            return outputdb

        proposed_db = inquirer.prompt(
            [
                inquirer.Path(
                    "outputdb",
                    message="Please choose a .db file to write to",
                    path_type=inquirer.Path.DIRECTORY,
                ),
            ]
        )

        if not proposed_db.endswith(".db"):
            console.print(f"please choose a .db file", style="yellow")
            continue
        return proposed_db


def main(
    db: str = "", outputdb: str = "", habits: List = [], yes: bool = False, version: bool = False
):
    if version:
        return __version__

    if not db:
        db = select_db()

    outputdb = outputdb or "output.db"
    outputdb = select_outputdb(outputdb, overwrite=yes)

    kwargs = {"inputdb": db, "outputdb": outputdb}
    console.print(f"Connecting to {db}", style="green")
    c = Converter(**kwargs)

    if not habits:
        console.print(f"Selecting habits interactively")
        include_archived = (
            Prompt.ask("Would you like to convert archived habits", choices=["y", "n"]) == "y"
        )
        bool_habits = c.get_bool_habits(include_archived)
        habits = inquirer.prompt(
            [
                inquirer.Checkbox(
                    "habits",
                    message="Which habits would you like to convert?",
                    choices=[h["name"] for h in bool_habits],
                ),
            ]
        )["habits"]
        # Standard Library
        import pdb

        pdb.set_trace()

    for habit in track(habits, description="Converting habits..."):
        errors = c.convert_bool_habit_to_num(habit_name=habit)
        if errors:
            console.print(errors, style="red")


if __name__ == "__main__":
    fire.Fire(main)
