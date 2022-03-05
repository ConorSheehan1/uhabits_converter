# Standard Library
import csv
import glob
import os
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

    def tearDown(self):
        # closing in memory db clears it
        self.converter.con.close()

    def test_get_bool_habits(self):
        actual = [v["name"] for v in self.converter.get_bool_habits()]
        expected = ["Coffee", "Gym", "Drink", "Program"]
        assert expected == actual

    # TODO: test convert_bool_habit_to_num
