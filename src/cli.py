
from typing import List
import fire
import os
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import track
import inquirer


from version import __version__
from convert import Converter

console = Console(color_system="auto")

def select_db():
    while True:
        proposed_db = Prompt.ask("Please choose a .db file to read from")
        if not os.path.exists(proposed_db):
            console.print(f"could not find file {proposed_db}", style="yellow")
            continue
        if not proposed_db.endswith('.db'):
            console.print(f"please choose a .db file", style="yellow")
            continue
        return proposed_db

def overwrite_file(path: str):
    Prompt.ask(f"{path} already exists. Would you like to overwrite it?", choices=["y", "n"]) == "y"

def select_outputdb(outputdb, overwrite: bool = False):
    while True:
        if not os.path.exists(outputdb):
            return outputdb

        if overwrite or overwrite_file(outputdb):
            return outputdb

        proposed_db = Prompt.ask("Please choose a .db file to write to")
        if os.path.exists(proposed_db) or not proposed_db:
            continue
        if not proposed_db.endswith('.db'):
            console.print(f"please choose a .db file", style="yellow")
            continue
        return proposed_db


def main(db: str = "", outputdb: str = '', habits: List = [], yes: bool=False, version: bool=False):
    if version:
        return __version__

    if not db:
        db = select_db()

    outputdb = outputdb or "output.db"
    outputdb = select_outputdb(outputdb, overwrite=yes)

    kwargs = {"inputdb": db ,"outputdb": outputdb}
    console.print(f"Connecting to {db}", style="green")
    c = Converter(**kwargs)

    if not habits:
        c.get_bool_habits()

    for habit in track(habits, description="Processing..."):
        c.convert_bool_habit_to_num(habit_name=habit)


if __name__ == "__main__":
    fire.Fire(main)
