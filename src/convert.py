# Standard Library
import shutil
import sqlite3
from typing import Literal, Optional, Union


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
        self.preserve_options = ["logic", "graph", "none", "custom"]

    def get_bool_habits(self, sort="position", include_archived=False) -> sqlite3.Cursor:
        where = f"type IS {self.bool_habit_type}"
        if not include_archived:
            where += " AND archived IS 0"
        return self.cursor.execute(f"SELECT * FROM Habits WHERE {where} ORDER BY {sort};")

    def update_target_preserve_graph(self, habit: dict) -> dict:
        # Keep freq_num whatever it already was, even though through the UI it is always 1 for numeric habits.
        # 7 every week is closer to 1 every day for graph
        if habit["freq_num"] == 1:
            return {"freq_den": 7, "target_value": 7}
        return {"target_value": habit["freq_num"]}

    def update_target_preserve_logic(self, habit: dict) -> dict:
        # freq_num is always 1 for numeric habits created through UI.
        # freq_den sets every day, week, or month, target_value sets how many times in that interval.
        return {"freq_num": 1, "target_value": habit["freq_num"]}

    def convert_bool_habit_to_num(
        self,
        habit_name: str,
        old_value: int = 2,
        new_value: int = 1000,
        preserve: str = "logic",
        target_value: Optional[int] = None,
    ) -> Union[str, Literal[False]]:
        """
        habit_name: name of habit
        old_value: extra safeguard for updating repetitions. rep must have habit id, and old_value (default to 2 for boolean reps).
        new_value: new value for repetition. default is 1000, equivalent to 1 in UI for float approximation.
        preserve: strategy for changing habit freq_den, freq_num, and target_value.
            logic: treat habit as if it was created as numeric from the beginning.
            graph: try to keep graphs the same but convert to numeric.
            none: do not update field.
            custom: use custom target_value.
        target_value: custom target_value. only use if preserve is 'custom'.
        """
        if preserve not in self.preserve_options:
            return f"preserve {preserve} must be one of {self.preserve_options}"
        if target_value is not None and preserve != "custom":
            return f"preserve must be 'custom' to set target_value"

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
            return f"Could not find habit with name '{habit_name}'"
        habit = dict(data)
        # some variance in schema, can be capitalized or not. see issue #6
        if "Id" in habit:
            habit_id = habit["Id"]
            where_habit_str = f"Id IS {habit['Id']}"
        else:
            habit_id = habit["id"]
            where_habit_str = f"id IS {habit['id']}"
        if habit["type"] != self.bool_habit_type:
            return f"Could not find habit with type ${self.bool_habit_type} and name '{habit_name}'"

        if preserve == "logic":
            update_dict = self.update_target_preserve_logic(habit)
        if preserve == "graph":
            update_dict = self.update_target_preserve_graph(habit)
        if preserve == "custom":
            update_dict = {"target_value": target_value}
        if preserve != "none":
            print_dict = {k: habit[k] for k in ["name", "freq_den", "freq_num", "target_value"]}
            update_str = ", ".join([f"{k} = {v}" for k, v in update_dict.items()])
            print(f"found {print_dict}")
            print(f"\tupdating {update_dict} ...")
            self.cursor.execute(
                f"UPDATE Habits Set {update_str} where {where_habit_str} AND TYPE IS {self.bool_habit_type};"
            )

        # update habit type
        self.cursor.execute(
            f"UPDATE Habits Set type = 1 where {where_habit_str} AND TYPE IS {self.bool_habit_type};"
        )

        # update reps
        self.cursor.execute(
            f"""
            UPDATE Repetitions
            SET value = {new_value}
            WHERE habit is {habit_id} AND value IS {old_value};
            """
        )

        # save
        self.con.commit()
        return False
