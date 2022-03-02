# Standard Library
import os
import sqlite3

base_path = os.path.dirname(os.path.abspath(__file__))
con = sqlite3.connect(os.path.join(base_path, "test.db"))
con.row_factory = sqlite3.Row  # use dict type, not tuple
cursor = con.cursor()


# just update gym
def convert_bool_habit_to_num(
    habit_name: str, old_value: int = 2, new_value: int = 1000, bool_habit_type: int = 0
):
    data = next(
        cursor.execute(
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
        cursor.execute(
            f"UPDATE Habits Set target_value = 1 where Id IS {habit['Id']} AND TYPE IS {bool_habit_type};"
        )

    # update habit type
    cursor.execute(
        f"UPDATE Habits Set type = 1 where Id IS {habit['Id']} AND TYPE IS {bool_habit_type};"
    )

    # update reps
    cursor.execute(
        f"""
    UPDATE Repetitions
    SET value = {new_value}
    WHERE habit is {habit['Id']} AND value IS {old_value};
    """
    )

    # save
    con.commit()

