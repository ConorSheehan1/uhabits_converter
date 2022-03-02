# Standard Library
import shutil
import sqlite3


class Converter:
    def __init__(self, inputdb: str, outputdb: str = 'output.db'):
        shutil.copy(inputdb, outputdb) # create copy of db to modify
        self.con = sqlite3.connect(outputdb)
        self.con.row_factory = sqlite3.Row  # use dict type, not tuple
        self.cursor = self.con.cursor()

    def get_bool_habits():
        return self.cursor.execute(f"SELECT * FROM Habits WHERE type IS {bool_habit_type};")

    def convert_bool_habit_to_num(
        self, habit_name: str, old_value: int = 2, new_value: int = 1000, bool_habit_type: int = 0
    ):
        # TODO: pass habit_id, handle duplicate habits with same name
        # different new_value may require change to sqlite_repetitions table?
        data = next(
            self.cursor.execute(
                f"SELECT * FROM Habits WHERE type IS {bool_habit_type} AND name IS '{habit_name}';"
            ),
            None,
        )
        if not data:
            print(f"Could not find habit with type {bool_habit_type} (boolean) and name {habit_name}")
            return

        habit = dict(data)
        print(f"updating {habit['name']}")

        # update habit target_value if necessary
        if habit["target_value"] < 1:
            # TODO: find value so charts match old boolean habbit
            # 1 too low, 10 too high?
            print(f"found target value of {habit['target_value']} < 1, updating...")
            self.cursor.execute(
                f"UPDATE Habits Set target_value = 1 where Id IS {habit['Id']} AND TYPE IS {bool_habit_type};"
            )

        # update habit type
        self.cursor.execute(
            f"UPDATE Habits Set type = 1 where Id IS {habit['Id']} AND TYPE IS {bool_habit_type};"
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

