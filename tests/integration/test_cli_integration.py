# Standard Library
import os
import unittest

from src.cli import cli


class TestSelectOutputDB(unittest.TestCase):
    def setUp(self):
        self.inputdb = "./tests/data/input.db"
        self.outputdb = "./tests/data/output.db"

    def tearDown(self):
        os.remove(self.outputdb)

    def test_cli(self):
        """
        simple test to check cli generates output.db without error.
        this may break for a variety of reasons.
        """
        assert os.path.isfile(self.outputdb) == False
        cli(
            inputdb=self.inputdb,
            outputdb=self.outputdb,
            habits=["Gym", "Drink", "Sweets", "Coffee"],
        )
        assert os.path.isfile(self.outputdb) == True
