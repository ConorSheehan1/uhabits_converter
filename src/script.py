import sqlite3
import os

base_path = os.path.dirname(os.path.abspath(__file__))
con = sqlite3.connect(os.path.join(base_path, 'test.db'))
con.row_factory = sqlite3.Row # use dict type, not tuple
cursor = con.cursor()


# just update gym
def convert_bool_habit_to_num(habit_name: str, old_value:int=2, new_value:int=1000):
    habit = [dict(v) for v in cursor.execute(f"SELECT Id, name, type FROM Habits WHERE type IS 0 AND name IS '{habit_name}';")][0]
    print(f"updating {habit['name']}")
    cursor.execute(f"UPDATE Habits Set type = 1 where Id IS {habit['Id']} AND TYPE IS 0;")

    cursor.execute(f"""
    UPDATE Repetitions
    SET value = {new_value}
    WHERE habit is {habit['Id']} AND value IS {old_value};
    """)

    con.commit()
    print("done")


convert_bool_habit_to_num('Drink')
convert_bool_habit_to_num('Coffee')
convert_bool_habit_to_num('P')
convert_bool_habit_to_num('Bash')

# # cast row to dict for better repr
# boolean_habbits = [dict(v) for v in cursor.execute("SELECT Id, name FROM Habits where type is 0")]

# for habbit in boolean_habbits:
#     print(habbit["name"])
#     print([dict(v) for v in cursor.execute(f"SELECT * FROM Repetitions where habit is {habbit['Id']}")])

