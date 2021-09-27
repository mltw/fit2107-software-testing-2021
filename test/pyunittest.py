from app.calculator import *
import unittest
import datetime

class TestCalculator(unittest.TestCase):

    # you may create more test methods
    # you may add parameters to test methods
    # this is an example
    def test_cost_v2(self):
        self.calculator = Calculator(5000, "14/09/2021")
        self.calculator = Calculator(5000, "14/9/2021")
        # self.assertEqual(self.calculator.cost_calculation("", "", "", "", ""), "")
        # start time before peak, end time before peak, single day
        self.assertEqual(self.calculator.cost_calculation_v2(0,100,20,50,350,"14/09/2021","05:30"),5.5)
        # start time before peak, end time before off peak, single day, multiple hour
        self.assertEqual(self.calculator.cost_calculation_v2(0,100,40,10,7.2,"14/09/2021","05:30"),2.43)
        # start time after 6, end time before 18, single day, within single hour
        self.assertEqual(self.calculator.cost_calculation_v2(0,100,40,50,350,"14/09/2021","06:10"),22)
        # starttime after 6, endtime before 18, single day, multiple hours
        self.assertEqual(self.calculator.cost_calculation_v2(0,100,40,10,7.2,"14/09/2021","06:10"),2.38)
        # starttime after 6, endtime after 18, single day, single hour
        self.assertEqual(self.calculator.cost_calculation_v2(0,100,40,50,350,"14/09/2021","17:55"),19.16)
        # starttime after 18, endtime before 18, single day, multiple hours
        self.assertEqual(self.calculator.cost_calculation_v2(0,100,40,10,7.2,"14/09/2021","19:00"),2.2)
        # starttime after 18, endtime after 18, single day, single hour
        self.assertEqual(self.calculator.cost_calculation_v2(0,100,40,50,350,"14/09/2021","19:00"),11)
        # starttime after 18, endtime after 18, single day, single hour
        self.assertEqual(self.calculator.cost_calculation_v2(0,100,40,50,350,"12/09/2021","23:55"),10.24)
        # starttime after 18, endtime next day , multiple hour
        self.assertEqual(self.calculator.cost_calculation_v2(0,100,40,10,7.2,"12/09/2021","23:55"),2.20)

    def test_cost_v3(self):
        self.calculator = Calculator(5000, "14/09/2021")
        # self.assertEqual(self.calculator.cost_calculation_v3(0, 100, 40, 10, 7.2, "12/09/2021", "23:55"), 2.20)
        # print(self.calculator.cost_calculation_v3())
        print(self.calculator.cost_calculation_v3(0, 100, 40, 10, 7.2, "14/09/2021", "14:00"))
        print(self.calculator.cost_calculation_v2(0, 100, 40, 10, 7.2, "14/09/2021", "14:00"))

    def test_calculate_solar_energy_new_w_cc(self):
        self.calculator = Calculator(7250, "22/02/2022")
        print(self.calculator.calculate_solar_energy_new_w_cc(start_date="22/02/2022", start_time="17:30",
                                                              initial_state=0, final_state=37.5,
                                                              capacity=4, power=2.0))

    def test_time(self):
        self.calculator = Calculator(5000, "14/09/2021")
        self.assertEqual(round(self.calculator.time_calculation(29, 37, 42, 3.6), 2), round(56 / 60, 2))
        self.assertEqual(round(self.calculator.time_calculation(7, 83, 56, 36), 2) * 60, 70.8)

    def test_holiday(self):
        self.calculator = Calculator(5000, "14/09/2021")
        # test public holiday
        self.assertEqual(self.calculator.is_holiday_v2(datetime.datetime(2021,12,25)), True)
        self.assertEqual(self.calculator.is_holiday_v2(datetime.datetime(2008,12,1)), True)
        # no holiday / weekdays
        self.assertEqual(self.calculator.is_holiday_v2(datetime.datetime(2021,9,14)), True)
        # test weekends
        self.assertEqual(self.calculator.is_holiday_v2(datetime.datetime(2021,9,12)), False)
        # test school holidays ?

    def test_peak(self):
        self.calculator = Calculator(5000, "14/09/2021")
        self.assertEqual(self.calculator.is_peak_v2(datetime.datetime(2008,12,1,14,4)), True)
        self.assertEqual(self.calculator.is_peak_v2(datetime.datetime(2008,12,1,14,6)), True)
        self.assertEqual(self.calculator.is_peak_v2(datetime.datetime(2008,12,1,14,18)), True)
        self.assertEqual(self.calculator.is_peak_v2(datetime.datetime(2008,12,1,5,59)), False)
        self.assertEqual(self.calculator.is_peak_v2(datetime.datetime(2008,12,1,18,1)), False)

    # def test_get_duration(self):
    #     self.calculator = Calculator(5000,"14/09/2021")
    #     self.calculator.get_duration("18:01")

    def test_get_sun_hour(self):
        self.calculator = Calculator(5000, "10/09/2021")
        self.assertEqual(self.calculator.get_sun_hour("02/02/2021"), 7.6)
        self.assertEqual(self.calculator.get_sun_hour("22/02/2020"), 7.2)

        self.calculator = Calculator(6001, "25/12/2020")
        self.assertEqual(self.calculator.get_sun_hour("25/12/2020"), 8.6)

    def test_get_solar_energy_duration(self):
        self.calculator = Calculator(5000, "10/09/2021")
        self.calculator.get_solar_energy_duration("18:01")

    # def test_get_cloud_cover(self):
    #     self.calculator = Calculator(5000,"14/09/2021")
    #     self.calculator.get_cloud_cover()

    # def test_get_cloud_cover(self):
    #     self.calculator = Calculator(5000,"14/09/2021")
    #     self.calculator.calculate_solar_energy()
    def test_power(self):
        self.calculator = Calculator(5000, "14/09/2021")
        self.assertEqual(self.calculator.get_power(1), 2.0)
        self.assertEqual(self.calculator.get_power(2), 3.6)
        self.assertEqual(self.calculator.get_power(3), 7.2)
        self.assertEqual(self.calculator.get_power(4), 11)
        self.assertEqual(self.calculator.get_power(5), 22)
        self.assertEqual(self.calculator.get_power(6), 36)
        self.assertEqual(self.calculator.get_power(7), 90)
        self.assertEqual(self.calculator.get_power(8), 350)

    def test_price(self):
        self.calculator = Calculator(5000, "14/09/2021")
        self.assertEqual(self.calculator.get_price(1), 5)
        self.assertEqual(self.calculator.get_price(2), 7.5)
        self.assertEqual(self.calculator.get_price(3), 10)
        self.assertEqual(self.calculator.get_price(4), 12.5)
        self.assertEqual(self.calculator.get_price(5), 15)
        self.assertEqual(self.calculator.get_price(6), 20)
        self.assertEqual(self.calculator.get_price(7), 30)
        self.assertEqual(self.calculator.get_price(8), 50)

    def test_get_cloud_cover(self):
        self.calculator = Calculator(5000, "22/02/2020")
        self.assertEqual(self.calculator.get_cloud_cover("22/02/2020", "17:30", "17:59"), 1)
        self.assertEqual(self.calculator.get_cloud_cover("22/02/2020", "18:00", "18:26"), 0)
        self.assertEqual(self.calculator.get_cloud_cover("22/02/2020", "00:00", "00:59"), 0)
        self.assertRaises(ValueError,
                          lambda: self.calculator.get_cloud_cover("24/02/2020", "23:15", "23:05"))
        self.assertRaises(ValueError,
                          lambda: self.calculator.get_cloud_cover("24/02/2020", "23:15", "21:05"))

    def test_get_day_light_length(self):
        self.calculator = Calculator(5000, "02/02/2021")
        self.assertAlmostEqual(self.calculator.get_day_light_length("02/02/2021"), 13.77, 2)

        self.calculator = Calculator(5000, "22/02/2020")
        self.assertAlmostEqual(self.calculator.get_day_light_length("22/02/2020"), 13.13, 2)

        self.calculator = Calculator(6001, "25/12/2020")
        self.assertAlmostEqual(self.calculator.get_day_light_length("25/12/2020"), 14.23, 2)

    def test_calculate_solar_energy_within_a_day(self):
        self.calculator = Calculator(6001, "25/12/2020")
        # self.assertAlmostEqual(self.calculator.calculate_solar_energy_within_a_day("25/12/2020", "08:00", "09:00"),
        #                        6.04, 1)

        # print(self.calculator.get_duration("1030", "1100"))
        print(self.calculator.calculate_solar_energy_within_a_day_by_hour("25/12/2020", "23:45", "00:30"))

        print(self.calculator.calculate_solar_energy_new(start_date="01/08/2021", start_time="11:00",
                                                         initial_state=0, final_state=100,
                                                         capacity=90, power=2.0))
        print(self.calculator.calculate_solar_energy_new(start_date="01/08/2021", start_time="07:30",
                                                         initial_state=90, final_state=100,
                                                         capacity=90, power=2.0))

    # "", "", , , ,
    # "01/08/2021", "07:30", 90, 100, 90, 2.0

    # def test_calculate_solar_energy(self):
    #     self.calculator = Calculator(6001, "25/12/2020")
    #     self.assertAlmostEqual(self.calculator.calculate_solar_energy("25/12/2020", "08:00", 20, 80, 82, 350), 0.85, 1)
    #
    #     # single day start time before sunrise, end time before sunrise
    #     self.assertEqual(self.calculator.calculate_solar_energy("01/08/2021", "06:00", 90, 100, 90, 90),0.0)
    #
    #     # single day start time before sunrise, end time between sunrise and sunset
    #     self.assertAlmostEqual(self.calculator.calculate_solar_energy("01/08/2021", "06:00", 90, 100, 90, 2.0), 8.995, 3)
    #
    #     # single day start time before sunrise, end time after sunset
    #     self.assertAlmostEqual(self.calculator.calculate_solar_energy("01/08/2021", "07:00", 0,30 ,90 , 2.0), 28, 1)
    #
    #     # single day start time after sunrise and sunset
    #     self.assertEqual(self.calculator.calculate_solar_energy("01/08/2021", "18:00", 90,100 ,90 , 90),0.0)
    #
    #     # single day start time after sunrise before sunset end time before sunset
    #     self.assertAlmostEqual(self.calculator.calculate_solar_energy("01/08/2021", "07:30", 90,100 ,90 , 2.0),11.9,1)
    #
    #     # single day start time after sunrise before sunset end time after sunset
    #     self.assertAlmostEqual(self.calculator.calculate_solar_energy("01/08/2021", "07:30", 0,30 ,90 , 2.0),26.94,2)
    #
    #     # multiple days start time after sunset end time before sunrise
    #     self.assertEqual(self.calculator.calculate_solar_energy("01/08/2021", "18:00", 0,80 ,90 , 2.0), 27)
    #
    #     # multiple days start time before sunrise end time after sunset ERR
    #     self.assertEqual(self.calculator.calculate_solar_energy("01/08/2021", "06:00", 0,90,90, 2.0), 55)
    #
    #     # multiple days start time between sunrise and sunset , end time between sunset and sunrise ERR
    #     self.assertAlmostEqual(self.calculator.calculate_solar_energy("01/08/2021", "11:00", 0,100 ,90, 2.0), 47.227, 2)

    if __name__ == "__main__":
        pass
