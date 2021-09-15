from app.calculator import *
import unittest


class TestCalculator(unittest.TestCase):

    # you may create more test methods
    # you may add parameters to test methods
    # this is an example
    def test_cost(self):

        self.calculator = Calculator(5000,"14/09/2021")
        self.calculator = Calculator(5000,"14/9/2021")
        print(self.calculator.weather_data)
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
        self.assertEqual(self.calculator.peak_period("18:01",7,83,56,36),0)
        # test starting from non-peak (4am) ends on non-peak on same day
        self.assertEqual(self.calculator.peak_period("01:50",7,83,56,36),0)
        # test starting from non-peak (6am) ends on peak on different day
        total = self.calculator.time_calculation(0,100,100,0.8)
        total_time = (self.calculator.time_calculation(0,100,100,0.8)+5.83333) - 24
        day = total_time//24
        remained_time = (total_time)%24
        add = 0
        if remained_time >= 18:
            add = 12
        else :
            if remained_time < 6 :
                add = 0
            else:
                add = remained_time - 6
        self.assertEqual(self.calculator.peak_period("05:50",0,100,100,0.8),int((12+day*12+add)*100/total))
        # test starting from non-peak (6pm) ends on peak on different day
        total = self.calculator.time_calculation(0,100,100,0.8)
        total_time = (self.calculator.time_calculation(0,100,100,0.8)+18) - 24
        day = total_time//24
        remained_time = (total_time)%24
        add = 0
        if remained_time >= 18:
            add = 12
        else :
            if remained_time < 6 :
                add = 0
            else:
                add = remained_time - 6
        self.assertEqual(self.calculator.peak_period("18:00",0,100,100,0.8),int((0+day*12+add)*100/total))
        # test starting from non-peak (6am) ends on non_peak on different day
        # test starting from non-peak (6pm) ends on non_peak on different day
        # test starting from peak ends on non_peak on same day
        # test starting from peak ends on peak on same day
        total = self.calculator.time_calculation(0,100,100,0.8)
        total_time = (self.calculator.time_calculation(0,100,100,0.8)+4) - 24
        day = total_time//24
        remained_time = (total_time)%24
        if remained_time >= 18:
            add = 12
        else :
            if remained_time < 6 :
                add = 0
            else:
                add = remained_time - 6
        self.assertEqual(self.calculator.peak_period("04:00",0,100,100,0.8),int((12+day*12+add)*100/total))
        # test starting from peak ends on non_peak on different day
        # test starting from peak ends on peak on different day

    # def test_get_duration(self):
    #     self.calculator = Calculator(5000,"14/09/2021")
    #     self.calculator.get_duration("18:01")

    def test_get_sun_hour(self):
        self.calculator = Calculator(5000,"10/09/2021")
        self.calculator.get_sun_hour()

    def test_get_solar_duration(self):
        self.calculator = Calculator(5000,"10/09/2021")
        self.calculator.get_solar_energy_duration("18:01")

    def test_get_cloud_cover(self):
        self.calculator = Calculator(5000,"14/09/2021")
        self.calculator.get_cloud_cover()

    def test_get_cloud_cover(self):
        self.calculator = Calculator(5000,"14/09/2021")
        self.calculator.calculate_solar_energy()
    def test_power(self):
        self.calculator = Calculator(5000,"14/09/2021")
        self.assertEqual(self.calculator.get_power(1),2.0)
        self.assertEqual(self.calculator.get_power(2),3.6)
        self.assertEqual(self.calculator.get_power(3),7.2)
        self.assertEqual(self.calculator.get_power(4),11)
        self.assertEqual(self.calculator.get_power(5),22)
        self.assertEqual(self.calculator.get_power(6),36)
        self.assertEqual(self.calculator.get_power(7),90)
        self.assertEqual(self.calculator.get_power(8),350)
    def test_price(self):
        self.calculator = Calculator(5000,"14/09/2021")
        self.assertEqual(self.calculator.get_price(1),5)
        self.assertEqual(self.calculator.get_price(2),7.5)
        self.assertEqual(self.calculator.get_price(3),10)
        self.assertEqual(self.calculator.get_price(4),12.5)
        self.assertEqual(self.calculator.get_price(5),15)
        self.assertEqual(self.calculator.get_price(6),20)
        self.assertEqual(self.calculator.get_price(7),30)
        self.assertEqual(self.calculator.get_price(8),50)

    def test_get_cloud_cover(self):
        self.calculator = Calculator(5000, "22/02/2020")
        self.assertEqual(self.calculator.get_cloud_cover("17:30", "18:15"), 1)
        self.assertEqual(self.calculator.get_cloud_cover("17:30", "17:59"), 1)
        self.assertEqual(self.calculator.get_cloud_cover("18:00", "18:26"), 0)
        self.assertEqual(self.calculator.get_cloud_cover("00:00", "00:59"), 0)

    if __name__ == "__main__":
        pass
