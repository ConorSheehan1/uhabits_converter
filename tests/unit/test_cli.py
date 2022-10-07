# Standard Library
import unittest

from src.cli import select_outputdb


class TestSelectOutputDB(unittest.TestCase):
    # def setUp(self):

    # def tearDown(self):

    def test_valid_first_pass(self):
        # TODO: stub os to ensure check always responds that file does not exist
        outputdb = "output_that_does_not_exist.db"
        assert select_outputdb(outputdb, "input.db") == outputdb
