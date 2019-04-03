from django.test import TestCase

from app.calc import add, subtract


class CalcTests(TestCase):

    def test_add_numbers(self):
        """Testing that two number are added together"""
        self.assertEqual(add(3, 8), 11)

    def test_subtract_numbers(self):
        """Testing that vlues are subtracted"""
        self.assertEqual(subtract(5, 11), 6)
