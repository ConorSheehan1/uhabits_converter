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
    db: str = "",
    outputdb: str = "",
    habits: List = [],
    new_value: int = 1000,
    target_value: int = 7,
    yes: bool = False,
    version: bool = False,
):
    """
    entrypoint for uhabits converter cli

    Args:
        db:             input database path. must already exist. if not provided, choose interactively.
        outputdb:       output database path. if already exists, confirm overwrite.
        habits:         list of boolean habits to convert to numeric. if not provided, choose interactively.
        new_value:      new numeric value. default is 1000. sqlite has no float type, so large int is used for float precision. e.g. if you want 2, set as 2000.
        target_value:   boolean habits with a target of 0 have an implicit scope of weekly, choose 7 by default.
        yes:            answer yes to all prompts.
        version:        print version.
    """
    if version:
        return __version__

    if not any([isinstance(habits, v) for v in [list, tuple]]):
        console.print(
            f"habits must be a list or tuple. got {type(habits)}. always include commas, even for a single habit. e.g. cli --habits=Gym,"
        )
        return False

    if not db:
        db = select_db()

    outputdb = outputdb or "output.db"
    outputdb = select_outputdb(outputdb, overwrite=yes)

    kwargs = {"inputdb": db, "outputdb": outputdb}
    console.print(f"Reading from {db}, writing to {outputdb}", style="green")
    c = Converter(**kwargs)

    if not habits:
        console.print(f"Selecting habits interactively")
        include_archived = (
            Prompt.ask("Would you like to convert archived habits", choices=["y", "n"]) == "y"
        )
        bool_habits = c.get_bool_habits(include_archived=include_archived, sort="name")
        habits = inquirer.prompt(
            [
                inquirer.Checkbox(
                    "habits",
                    message="Which habits would you like to convert?",
                    choices=[h["name"] for h in bool_habits],
                ),
            ]
        )["habits"]

    for habit in track(habits, description="Converting habits..."):
        errors = c.convert_bool_habit_to_num(
            habit_name=habit, new_value=new_value, target_value=target_value
        )
        if errors:
            console.print(errors, style="red")


if __name__ == "__main__":
    fire.Fire(main)
