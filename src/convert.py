# Standard Library
import shutil
import sqlite3
from typing import Literal, Union


class Converter:
    def __init__(
        self,
        inputdb: str,
        outputdb: str = "output.db",
        create_outputdb: bool = True,
        bool_habit_type: int = 0,
    ):
        if create_outputdb:
            shutil.copy(inputdb, outputdb)  # create copy of db to modify
        self.bool_habit_type = bool_habit_type
        self.con = sqlite3.connect(outputdb)
        self.con.row_factory = sqlite3.Row  # use dict type, not tuple
        self.cursor = self.con.cursor()

    def get_bool_habits(self, sort="position", include_archived=False) -> sqlite3.Cursor:
        where = f"type IS {self.bool_habit_type}"
        if not include_archived:
            where += " AND archived IS 0"
        return self.cursor.execute(f"SELECT * FROM Habits WHERE {where} ORDER BY {sort};")

    def convert_bool_habit_to_num(
        self, habit_name: str, old_value: int = 2, new_value: int = 1000, target_value: int = 7
    ) -> Union[str, Literal[False]]:
        # TODO: pass habit_id, handle duplicate habits with same name
        # different new_value may require change to sqlite_repetitions table?
        data = next(
            self.cursor.execute(
                f"SELECT * FROM Habits WHERE type IS {self.bool_habit_type} AND name IS '{habit_name}';"
            ),
            None,
        )
        # TODO: separate error for already numeric habit and no habit found
        if not data:
            return f"Could not find habit with type {self.bool_habit_type} (boolean) and name '{habit_name}'"

        habit = dict(data)

        # update habit target_value if necessary
        if habit["target_value"] < 1:
            # boolean habits with a target of 0 have an implicit scope of weekly, choose 7 by default
            print(
                f"found target value of {habit['target_value']} < 1, updating to {target_value}..."
            )
            self.cursor.execute(
                f"UPDATE Habits Set target_value = {target_value} where Id IS {habit['Id']} AND TYPE IS {self.bool_habit_type};"
            )

        # update habit type
        self.cursor.execute(
            f"UPDATE Habits Set type = 1 where Id IS {habit['Id']} AND TYPE IS {self.bool_habit_type};"
        )

        # update reps
        self.cursor.execute(
            f"""
            UPDATE Repetitions
            SET value = {new_value}
            WHERE habit is {habit['Id']} AND value IS {old_value};
            """
        )

        # save
        self.con.commit()
        return False
