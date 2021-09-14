from app.calculator import *
import unittest


class TestCalculator(unittest.TestCase):

    def setUp(self):
        self.calculator = Calculator()

    # you may create more test methods
    # you may add parameters to test methods
    # this is an example
    def test_cost(self):
        # self.assertEqual(self.calculator.cost_calculation("", "", "", "", ""), "")
        self.assertEqual(round(self.calculator.cost_calculation(29, 37, 42, True, True),2), 0.28)

    def test_time(self):
        self.assertEqual(round(self.calculator.time_calculation(29,37,42,3.6),2), round(56/60,2))

    def test_holiday(self):
        # test public holiday
        self.assertEqual(self.calculator.is_holiday("25/12/2021"),True)
        # no holiday / weekdays
        self.assertEqual(self.calculator.is_holiday("14/09/2021"),True)
        # test weekends
        self.assertEqual(self.calculator.is_holiday("12/09/2021"),False)
        # test school holidays ?

    def test_peak(self):
        pass

    # you may create test suite if needed
    if __name__ == "__main__":
        pass
