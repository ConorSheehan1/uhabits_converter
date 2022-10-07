# Standard Library
import glob
import os
from typing import List, Optional, Union

# Third party
import fire
import inquirer
from rich.console import Console
from rich.progress import track
from rich.prompt import Prompt

from src.convert import Converter
from src.version import __version__

console = Console(color_system="auto")


def select_db() -> str:
    cwd_interactive = False
    while True:
        # glob is not expensive and user may move files while prompt is still open, so check every loop
        db_files_in_cwd = glob.glob("*.db")
        if cwd_interactive:
            inquirer_args = [
                inquirer.List(
                    "inputdb",
                    message="choose an input .db file",
                    choices=list(db_files_in_cwd),
                ),
            ]
        else:
            inquirer_args = [
                inquirer.Path(
                    "inputdb",
                    message="choose an input .db file",
                    path_type=inquirer.Path.FILE,
                )
            ]
        proposed_db = inquirer.prompt(inquirer_args)["inputdb"]

        if not os.path.exists(proposed_db):
            console.print(f"{proposed_db} not found", style="yellow")
            # only allow interactive prompt is there are .db files in cwd
            if db_files_in_cwd:
                cwd_interactive = Prompt.ask(f"choose interactively?", choices=["y", "n"]) == "y"
            continue
        if not proposed_db.endswith(".db"):
            console.print(f"inputdb must end with .db", style="yellow")
            continue
        return proposed_db


def overwrite_file(path: str) -> bool:
    return Prompt.ask(f"{path} already exists. overwrite?", choices=["y", "n"]) == "y"


def select_outputdb(outputdb, inputdb, overwrite: bool = False) -> str:
    proposed_db = outputdb
    while True:
        if not proposed_db.endswith(".db"):
            console.print(f"outputdb must end with .db", style="yellow")
        else:
            if not os.path.exists(proposed_db):
                return proposed_db

            if proposed_db == inputdb:
                console.print(
                    f"outputdb can't be the same as inputdb. choose another .db file",
                    style="yellow",
                )
            elif overwrite or overwrite_file(proposed_db):
                return proposed_db

        proposed_db = inquirer.prompt(
            [
                inquirer.Path(
                    "outputdb",
                    message="choose an output .db file",
                    path_type=inquirer.Path.FILE,
                ),
            ]
        )["outputdb"]


def cli(
    inputdb: str = "",
    outputdb: str = "",
    habits: List = [],
    new_value: int = 1000,
    preserve: str = "logic",
    target_value: Optional[int] = None,
    yes: bool = False,
    version: bool = False,
):
    """
    entrypoint for uhabits converter cli

    Args:
        inputdb:             input database path. must already exist. if not provided, choose interactively.
        outputdb:       output database path. if already exists, confirm overwrite.
        habits:         list of boolean habits to convert to numeric. if not provided, choose interactively.
        preserve: strategy for changing habit freq_den, freq_num, and target_value.
            logic: treat habit as if it was created as numeric from the beginning.
            graph: try to keep graphs the same but convert to numeric.
            none: do not update field.
            custom: use custom target_value.
        target_value: custom target_value. only use if preserve is 'custom'.
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

    if not inputdb:
        inputdb = select_db()

    outputdb = outputdb or "output.db"
    outputdb = select_outputdb(outputdb, inputdb, overwrite=yes)

    console.print(f"Reading from {inputdb}, writing to {outputdb}", style="green")
    c = Converter(inputdb=inputdb, outputdb=outputdb)

    if not habits:
        console.print(f"Selecting habits interactively")
        include_archived = Prompt.ask("convert archived habits", choices=["y", "n"]) == "y"
        bool_habits = c.get_bool_habits(include_archived=include_archived, sort="name")
        while not habits:
            habits = inquirer.prompt(
                [
                    inquirer.Checkbox(
                        "habits",
                        message="choose habits to convert",
                        choices=[h["name"] for h in bool_habits],
                    ),
                ]
            )["habits"]
            if not habits:
                console.print(
                    f"no habits selected. make a selection using right arrow key. unselect using left arrow. navigate using up / down."
                )

    for habit in track(habits, description="Converting habits..."):
        errors = c.convert_bool_habit_to_num(
            habit_name=habit, new_value=new_value, preserve=preserve, target_value=target_value
        )
        if errors:
            console.print(errors, style="red")


def main():
    fire.Fire(cli)


if __name__ == "__main__":
    main()
