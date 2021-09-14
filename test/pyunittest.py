from app.calculator import *
import unittest


class TestCalculator(unittest.TestCase):

    # you may create more test methods
    # you may add parameters to test methods
    # this is an example
    def test_cost(self):
        self.calculator = Calculator(5000,"14/09/2021")
        # self.assertEqual(self.calculator.cost_calculation("", "", "", "", ""), "")
        self.assertEqual(round(self.calculator.cost_calculation(29, 37, 42, 100, True,7.5),2), 0.28)
        self.assertEqual(round(self.calculator.cost_calculation(7, 83, 56, 100, False,20),2), 8.51)
        self.assertEqual(round(self.calculator.cost_calculation(7, 83, 56, 0, False,20),2), 4.26)
        self.assertEqual(round(self.calculator.cost_calculation(7, 83, 56, 14, False,20),2), 4.85)
        self.assertRaises(AssertionError , self.calculator.cost_calculation ,7, 83, 56, -14, False,20)

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

    def test_peak_period(self):
        self.calculator = Calculator(5000,"14/09/2021")
        self.assertEqual(self.calculator.peak_period("17:50",7,83,56,36),14)
        # test multiple days charging
        self.assertEqual(self.calculator.peak_period("17:50",0,100,56,3.6),22)
        # test multiple days charging
        self.assertEqual(self.calculator.peak_period("17:50",0,100,100,0.8),48)
        self.assertEqual(self.calculator.peak_period("14:50",7,83,56,36),100)

        # test starting from non-peak (6am) ends on peak on same day
        self.assertEqual(self.calculator.peak_period("05:50",7,83,56,36),int((self.calculator.time_calculation(7,83,56,36)+5.83333 - 6.0)*100/self.calculator.time_calculation(7,83,56,36)))
        # test starting from non-peak (6pm) ends on non-peak on same day
        self.assertEqual(self.calculator.peak_period("18:00",7,83,56,36),0)
        # test starting from non-peak (4am) ends on non-peak on same day
        self.assertEqual(self.calculator.peak_period("18:50",7,83,56,36),0)

    # you may create test suite if needed
    if __name__ == "__main__":
        pass
