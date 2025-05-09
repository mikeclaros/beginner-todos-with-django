import unittest
import random
from mywebsite.todos.utils import filter_guest_accounts


class TestUtilityFunctions:
    class TestGuestFilter(unittest.TestCase):
        def test_guest_filter_function_filters_a_guest_name(self):
            name = "Guest1234"
            result = filter_guest_accounts(name)
            self.assertTrue(result)

            result = filter_guest_accounts("Guest12340")
            self.assertFalse(result)
