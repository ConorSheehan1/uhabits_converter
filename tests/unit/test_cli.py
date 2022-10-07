# Standard Library
import unittest

from src.cli import select_outputdb


class TestSelectOutputDB(unittest.TestCase):
    def test_returns_arg_if_not_exists(self):
        """
        if the output file does not exist yet, return it.
        """
        # TODO: stub os to ensure check always responds that file does not exist
        outputdb = "output_that_does_not_exist.db"
        assert select_outputdb(outputdb, "input.db") == outputdb
