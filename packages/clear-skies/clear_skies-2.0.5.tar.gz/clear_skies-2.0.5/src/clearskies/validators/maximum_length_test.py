import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from .maximum_length import MaximumLength


class MaximumLengthTest(unittest.TestCase):
    def setUp(self):
        self.maximum_length = MaximumLength(10)

    def test_check_length(self):
        error = self.maximum_length.check("model", "name", {"name": "1234567890"})  # type: ignore
        self.assertEqual("", error)
        error = self.maximum_length.check("model", "name", {"name": ""})  # type: ignore
        self.assertEqual("", error)
        error = self.maximum_length.check("model", "name", {})  # type: ignore
        self.assertEqual("", error)
        error = self.maximum_length.check("model", "name", {"name": "123456789"})  # type: ignore
        self.assertEqual("", error)
        error = self.maximum_length.check("model", "name", {"name": "12345678901"})  # type: ignore
        self.assertEqual("'name' must be at most 10 characters long.", error)
