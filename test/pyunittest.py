from app.calculator import *
import unittest


class TestCalculator(unittest.TestCase):

    # you may create more test methods
    # you may add parameters to test methods
    # this is an example
    def test_cost(self):
        self.calculator = Calculator(5000, "14/09/2021")
        self.calculator = Calculator(5000, "14/9/2021")
        # self.assertEqual(self.calculator.cost_calculation("", "", "", "", ""), "")
        self.assertEqual(round(self.calculator.cost_calculation(29, 37, 42, 1, 1, 7.5), 2), 0.28)
        self.assertEqual(round(self.calculator.cost_calculation(7, 83, 56, 1, 0, 20), 2), 8.51)
        self.assertEqual(round(self.calculator.cost_calculation(7, 83, 56, 0, 0, 20), 2), 4.26)
        self.assertEqual(round(self.calculator.cost_calculation(7, 83, 56, 0.14, 0, 20), 2), 4.85)
        self.assertRaises(AssertionError, self.calculator.cost_calculation, 7, 83, 56, -14, 1, 20)

    def test_time(self):
        self.calculator = Calculator(5000, "14/09/2021")
        self.assertEqual(round(self.calculator.time_calculation(29, 37, 42, 3.6), 2), round(56 / 60, 2))
        self.assertEqual(round(self.calculator.time_calculation(7, 83, 56, 36), 2) * 60, 70.8)

    def test_holiday(self):
        self.calculator = Calculator(5000, "14/09/2021")
        # test public holiday
        self.assertEqual(self.calculator.is_holiday("25/12/2021"), True)
        self.assertEqual(self.calculator.is_holiday("01/12/2008"), True)
        # no holiday / weekdays
        self.assertEqual(self.calculator.is_holiday("14/09/2021"), True)
        # test weekends
        self.assertEqual(self.calculator.is_holiday("12/09/2021"), False)
        # test school holidays ?

    def test_peak(self):
        self.calculator = Calculator(5000, "14/09/2021")
        self.assertEqual(self.calculator.is_peak("14:04"), True)
        self.assertEqual(self.calculator.is_peak("06:00"), True)
        self.assertEqual(self.calculator.is_peak("18:00"), True)
        self.assertEqual(self.calculator.is_peak("05:59"), False)
        self.assertEqual(self.calculator.is_peak("18:01"), False)

    def test_peak_period(self):
        self.calculator = Calculator(5000, "14/09/2021")
        self.assertEqual(self.calculator.peak_period("17:50", 7, 83, 56, 36), 0.1412)
        # test multiple days charging
        self.assertEqual(self.calculator.peak_period("17:50", 0, 100, 56, 3.6), 0.2288)
        # test multiple days charging
        self.assertEqual(self.calculator.peak_period("17:50", 0, 100, 100, 0.8), 0.4813)
        self.assertEqual(self.calculator.peak_period("14:50", 7, 83, 56, 36), 1)

        # test starting from non-peak (6am) ends on peak on same day
        self.assertEqual(self.calculator.peak_period("05:50", 7, 83, 56, 36), 0.8588)
        # test starting from non-peak (6pm) ends on non-peak on same day
        self.assertEqual(self.calculator.peak_period("18:00", 7, 83, 56, 36), 0)
        self.assertEqual(self.calculator.peak_period("18:01", 7, 83, 56, 36), 0)
        # test starting from non-peak (4am) ends on non-peak on same day
        self.assertEqual(self.calculator.peak_period("01:50", 7, 83, 56, 36), 0)
        # test starting from non-peak (6am) ends on peak on different day
        total = self.calculator.time_calculation(0, 100, 100, 0.8)
        total_time = (self.calculator.time_calculation(0, 100, 100, 0.8) + 5.83333) - 24
        day = total_time // 24
        remained_time = (total_time) % 24
        add = 0
        if remained_time >= 18:
            add = 12
        else:
            if remained_time < 6:
                add = 0
            else:
                add = remained_time - 6
        self.assertEqual(self.calculator.peak_period("05:50", 0, 100, 100, 0.8),
                         round((12 + day * 12 + add) / total, 4))
        # test starting from non-peak (6pm) ends on peak on different day
        total = self.calculator.time_calculation(0, 100, 100, 0.8)
        total_time = (self.calculator.time_calculation(0, 100, 100, 0.8) + 18) - 24
        day = total_time // 24
        remained_time = (total_time) % 24
        add = 0
        if remained_time >= 18:
            add = 12
        else:
            if remained_time < 6:
                add = 0
            else:
                add = remained_time - 6
        self.assertEqual(self.calculator.peak_period("18:00", 0, 100, 100, 0.8), (0 + day * 12 + add) / total)
        # test starting from non-peak (6am) ends on non_peak on different day
        # test starting from non-peak (6pm) ends on non_peak on different day
        # test starting from peak ends on non_peak on same day
        # test starting from peak ends on peak on same day
        total = self.calculator.time_calculation(0, 100, 100, 0.8)
        total_time = (self.calculator.time_calculation(0, 100, 100, 0.8) + 4) - 24
        day = total_time // 24
        remained_time = (total_time) % 24
        if remained_time >= 18:
            add = 12
        else:
            if remained_time < 6:
                add = 0
            else:
                add = remained_time - 6
        self.assertEqual(self.calculator.peak_period("04:00", 0, 100, 100, 0.8), (12 + day * 12 + add) / total)
        # test starting from peak ends on non_peak on different day
        # test starting from peak ends on peak on different day

    def test_holiday_temp(self):
        self.calculator = Calculator(5000, "14/09/2021")
        final_state = 100
        initial_state = 0
        capacity = 300
        power = 2.9
        # time is 103.45 hours
        time = (final_state - initial_state) / 100 * capacity / power
        # 18/09/2021 -- Weekend 106.45  03:00 --> 24:00  (21.03 hrs)
        # 19/09/2021 -- Weekend 82.45   (24hrs)
        # 20/09/2021 -- Weekday 58.45   (24hrs)
        # 21/09/2021 -- Weekday 34.45   (24hrs)
        # 22/09/2021 -- Weekday 10.45    (10.45hrs)
        # total time : 58.45
        # percentage : 58.45 / 103.45
        self.assertEqual(
            self.calculator.is_holiday_temp("18/09/2021", initial_state, final_state, capacity, power, "03:00"),
            round((58.45 / 103.45), 4))
        final_state = 100
        initial_state = 0
        capacity = 300
        power = 100
        # time is 3.0 hours
        time = (final_state - initial_state) / 100 * capacity / power
        # 18/09/2021 -- Weekend 3  03:00 --> 06:00  (3hrs)
        # total holiday time : 0
        # percentage : 0%
        self.assertEqual(
            self.calculator.is_holiday_temp("18/09/2021", initial_state, final_state, capacity, power, "03:00"), 0)
        # 20/09/2021 -- Weekday 3  03:00 --> 06:00  (3hrs)
        # total holiday time : 3
        # percentage : 1
        self.assertEqual(
            self.calculator.is_holiday_temp("20/09/2021", initial_state, final_state, capacity, power, "03:00"), 1)
        # test if minute is working for this case
        self.assertEqual(
            self.calculator.is_holiday_temp("20/09/2021", initial_state, final_state, capacity, power, "03:30"), 1)
        final_state = 100
        initial_state = 0
        capacity = 300
        power = 2.9
        # time is 103.45 hours
        time = (final_state - initial_state) / 100 * capacity / power
        # 21/09/2021 -- Weekday 106.45  03:00 --> 24:00  (21.00 hrs)
        # 22/09/2021 -- Weekday 82.45   (24hrs)
        # 23/09/2021 -- Weekday 58.45   (24hrs)
        # 24/09/2021 -- Weekday 34.45   (24hrs)
        # 25/09/2021 -- Weekend 10.45    (10.45hrs)
        # total time : 93
        # percentage : 93 / 103.45
        self.assertEqual(
            self.calculator.is_holiday_temp("21/09/2021", initial_state, final_state, capacity, power, "03:00"),
            round(93 / 103.45, 4))

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
        self.assertEqual(self.calculator.get_cloud_cover("22/02/2020", "17:30", "22/02/2020", "18:15"), 1)
        self.assertEqual(self.calculator.get_cloud_cover("22/02/2020", "17:30", "22/02/2020", "17:59"), 1)
        self.assertEqual(self.calculator.get_cloud_cover("22/02/2020", "18:00", "22/02/2020", "18:26"), 0)
        self.assertEqual(self.calculator.get_cloud_cover("22/02/2020", "00:00", "22/02/2020", "00:59"), 0)
        self.assertEqual(self.calculator.get_cloud_cover("22/02/2020", "23:15", "23/02/2020", "00:15"), 0)
        self.assertRaises(ValueError,
                          lambda: self.calculator.get_cloud_cover("24/02/2020", "23:15", "23/02/2020", "00:15"))
        self.assertRaises(ValueError,
                          lambda: self.calculator.get_cloud_cover("24/02/2020", "23:15", "24/02/2020", "23:05"))
        self.assertRaises(ValueError,
                          lambda: self.calculator.get_cloud_cover("24/02/2020", "23:15", "24/02/2020", "21:05"))

    def test_get_day_light_length(self):
        self.calculator = Calculator(5000, "02/02/2021")
        self.assertAlmostEqual(self.calculator.get_day_light_length("02/02/2021"), 13.77, 2)

        self.calculator = Calculator(5000, "22/02/2020")
        self.assertAlmostEqual(self.calculator.get_day_light_length("22/02/2020"), 13.13, 2)

        self.calculator = Calculator(6001, "25/12/2020")
        self.assertAlmostEqual(self.calculator.get_day_light_length("25/12/2020"), 14.23, 2)

    def test_calculate_solar_energy_within_a_day(self):
        self.calculator = Calculator(6001, "25/12/2020")
        self.assertAlmostEqual(self.calculator.calculate_solar_energy_within_a_day("25/12/2020", "08:00", "09:00"),
                               6.04, 1)

    def test_calculate_solar_energy(self):
        self.calculator = Calculator(6001, "25/12/2020")
        self.assertAlmostEqual(self.calculator.calculate_solar_energy("25/12/2020", "08:00", 20, 80, 82, 350), 0.85, 1)

        # single day start time before sunrise, end time before sunrise
        self.assertEqual(self.calculator.calculate_solar_energy("01/08/2021", "06:00", 90, 100, 90, 90),0.0)

        # single day start time before sunrise, end time between sunrise and sunset
        self.assertEqual(self.calculator.calculate_solar_energy("01/08/2021", "06:00", 90, 100, 90, 2.0), 8.99527559055118)

        # single day start time before sunrise, end time after sunset
        self.assertAlmostEqual(self.calculator.calculate_solar_energy("01/08/2021", "07:00", 0,30 ,90 , 2.0), 28, 1)

        # single day start time after sunrise and sunset
        self.assertEqual(self.calculator.calculate_solar_energy("01/08/2021", "18:00", 90,100 ,90 , 90),0.0)

        # single day start time after sunrise before sunset end time before sunset
        self.assertAlmostEqual(self.calculator.calculate_solar_energy("01/08/2021", "07:30", 90,100 ,90 , 2.0),11.9,1)

        # single day start time after sunrise before sunset end time after sunset
        self.assertAlmostEqual(self.calculator.calculate_solar_energy("01/08/2021", "07:30", 0,30 ,90 , 2.0),26.94,2)

        # multiple days start time after sunset end time before sunrise
        self.assertEqual(self.calculator.calculate_solar_energy("01/08/2021", "18:00", 0,80 ,90 , 2.0), 27)

        # multiple days start time before sunrise end time after sunset ERR
        self.assertEqual(self.calculator.calculate_solar_energy("01/08/2021", "06:00", 0,90,90, 2.0), 56)

        # multiple days start time between sunrise and sunset , end time between sunset and sunrise ERR
        self.assertAlmostEqual(self.calculator.calculate_solar_energy("01/08/2021", "11:00", 0,100 ,90, 2.0), 47.013, 2)

    if __name__ == "__main__":
        pass
