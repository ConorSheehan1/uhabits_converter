# Standard Library
import csv
import glob
import os
import sqlite3
import unittest
from typing import List

# Third party
import pandas

from src.convert import Converter


class TestConverter(unittest.TestCase):
    def setUp(self):
        cwd = os.path.abspath(os.path.dirname(__file__))
        data_dir = os.path.join(cwd, "..", "data")
        csv_glob = os.path.join(data_dir, "*.csv")
        # create sql db in memory for test
        self.converter = Converter(inputdb="", outputdb=":memory:", create_outputdb=False)
        for csv_file in glob.glob(csv_glob):
            self.load_csv_to_table(csv_file)

    def load_csv_to_table(self, csv_path: str):
        table = os.path.basename(csv_path).replace(".csv", "")
        df = pandas.read_csv(csv_path)
        df.to_sql(table, self.converter.con)

    def get_habit_by_name(self, name: str) -> dict:
        return dict(
            next(self.converter.cursor.execute(f"SELECT * FROM Habits WHERE name IS '{name}';"))
        )

    def get_entries_by_id(self, habit_id: int) -> List[dict]:
        return [
            dict(rep)
            for rep in self.converter.cursor.execute(
                f"SELECT * FROM Repetitions WHERE habit IS {habit_id};"
            )
        ]

    def tearDown(self):
        # closing in memory db clears it
        self.converter.con.close()

    def test_get_bool_habits(self):
        actual = [v["name"] for v in self.converter.get_bool_habits()]
        expected = ["Coffee", "Gym", "Drink", "Program"]
        assert expected == actual

    def test_convert_bool_habit_to_num(self):
        # assert coffee and reps are boolean
        habit_before = self.get_habit_by_name("Coffee")
        reps_before = self.get_entries_by_id(habit_before["Id"])
        assert habit_before["type"] == 0
        assert all([rep["value"] == 2 for rep in reps_before])

        # Assert all boolean habits
        bool_habits_before = [v["name"] for v in self.converter.get_bool_habits()]
        assert ["Coffee", "Gym", "Drink", "Program"] == bool_habits_before

        self.converter.convert_bool_habit_to_num("Coffee")

        # Assert only Coffee has changed
        bool_habits_after = [v["name"] for v in self.converter.get_bool_habits()]
        assert ["Gym", "Drink", "Program"] == bool_habits_after

        # assert coffee and reps are numeric
        habit_after = self.get_habit_by_name("Coffee")
        reps_after = self.get_entries_by_id(habit_after["Id"])
        assert habit_after["type"] == 1
        assert all([rep["value"] == 1000 for rep in reps_after])
