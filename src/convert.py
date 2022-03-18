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
        self,
        habit_name: str,
        old_value: int = 2,
        new_value: int = 1000,
        target_value: Union[int, bool] = True,
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

        expected_habit_targets = {1: 365}

        if target_value is not False:
            if target_value is not True:
                # target value is neither True nor False, must be int
                # TODO: probably need to update freq_num/freq_den too
                new_target = target_value
            else:
                freq_num = 1
                # TODO: coffee case
                # bool          {freq_den: 7 freq_num: 5, target_value: 0}
                # numeric curr  {freq_den: 7, freq_num: 1, target_value: 5}
                # numeric best  {freq_den: 7, freq_num: 5, target_value: 7}
                if habit["freq_num"] == 1:
                    # 7 every week is closer to 1 every day for graph
                    new_target = 7
                    freq_den = 7
                else:
                    # otherwise use freq_num as target and set freq_num to 1.
                    # TODO: drink case
                    # e.g. twice per week as boolean is {freq_den:7, freq_num: 2, target_value: 0}
                    # as numeric is {freq_den: 7, freq_num: 1, target_value: 2}
                    new_target = habit["freq_num"]
                    freq_den = None
            print_dict = {k: habit[k] for k in ["name", "target_value", "freq_num"]}
            update_dict = {"target_value": new_target, "freq_num": freq_num}
            if freq_den is not None:
                update_dict["freq_den"] = freq_den

            update_str = ", ".join([f"{k} = {v}" for k, v in update_dict.items()])
            print(
                f"found {print_dict}{' ':<{75 - len(str(print_dict))}} updating {update_dict} ..."
            )
            self.cursor.execute(
                f"UPDATE Habits Set {update_str} where Id IS {habit['Id']} AND TYPE IS {self.bool_habit_type};"
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
