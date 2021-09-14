from ..app.calculator import *
import unittest


class TestCalculator(unittest.TestCase):

    # you may create more test methods
    # you may add parameters to test methods
    # this is an example
    def test_cost(self):
        self.calculator = Calculator(5000,"14/09/2021")
        # self.assertEqual(self.calculator.cost_calculation("", "", "", "", ""), "")
        self.assertEqual(round(self.calculator.cost_calculation(29, 37, 42, True, True,7.5),2), 0.28)
        self.assertEqual(round(self.calculator.cost_calculation(7, 83, 56, True, False,20),2), 8.51)
        pass

    def test_time(self):
        self.calculator = Calculator(5000,"14/09/2021")
        self.assertEqual(round(self.calculator.time_calculation(29,37,42,3.6),2), round(56/60,2))
        self.assertEqual(round(self.calculator.time_calculation(7,83,56,36),2)*60, 70.8)

    def test_holiday(self):
        self.calculator = Calculator(5000,"14/09/2021")
        #test public holiday
        self.assertEqual(self.calculator.is_holiday("25/12/2021"),True)
        self.assertEqual(self.calculator.is_holiday("01/12/2008"),True)
        # no holiday / weekdays
        self.assertEqual(self.calculator.is_holiday("14/09/2021"),True)
        # test weekends
        self.assertEqual(self.calculator.is_holiday("12/09/2021"),False)
        # test school holidays ?

    def test_peak(self):
        self.calculator = Calculator(5000,"14/09/2021")
        self.assertEqual(self.calculator.is_peak("14:04"),True)
        self.assertEqual(self.calculator.is_peak("06:00"),True)
        self.assertEqual(self.calculator.is_peak("18:00"),True)
        self.assertEqual(self.calculator.is_peak("05:59"),False)
        self.assertEqual(self.calculator.is_peak("18:01"),False)

    # you may create test suite if needed
    if __name__ == "__main__":
        pass
