import holidays
import datetime
import requests
import json
from datetime import time
class Calculator():
    # you can choose to initialise variables here, if needed.
    def __init__(self, postcode, date):
        location_link = "http://118.138.246.158/api/v1/location"
        postcode = str(postcode)
        postcode_PARAMS = {'postcode':postcode}
        location_r = requests.get(url=location_link,params=postcode_PARAMS)
        location_data = location_r.json()

        weather_link = "http://118.138.246.158/api/v1/weather"
        location_id = location_data[0]['id']
        date_time_obj = datetime.datetime.strptime(date, '%d/%m/%Y')
        month = str(date_time_obj.month)
        if len(month) != 2 :
            month = "0" + month
        new_date = str(date_time_obj.year) +  "-" + month + "-" + str(date_time_obj.day)
        weather_PARAMS = {'location' : location_id, 'date': new_date}
        weather_r = requests.get(url=weather_link,params=weather_PARAMS)
        self.weather_data = weather_r.json()

    # you may add more parameters if needed, you may modify the formula also.
    def cost_calculation(self, initial_state, final_state, capacity, peak_period, is_holiday,base_price):
        assert peak_period >= 0 and peak_period <= 100 , "Please provide a valid peak_period, must be between 0 and 100"
        non_peak = 0.5*(1-(peak_period/100))
        peak = (1*(peak_period/100))
        base_price =base_price*(non_peak+peak)

        if is_holiday:
            surcharge_factor = 1.1
        else:
            surcharge_factor = 1

        cost = (int(final_state) - int(initial_state)) / 100 * int(capacity) * base_price / 100 * surcharge_factor
        return cost

    # you may add more parameters if needed, you may also modify the formula.
    def time_calculation(self, initial_state, final_state, capacity, power):
        time = (int(final_state) - int(initial_state)) / 100 * int(capacity) / power
        return time


    # you may create some new methods at your convenience, or modify these methods, or choose not to use them.
    def is_holiday(self, start_date):
        aus_holidays = holidays.Australia()
        date_time_obj = datetime.datetime.strptime(start_date, '%d/%m/%Y')
        return date_time_obj in aus_holidays or date_time_obj.weekday() <= 4

    def is_peak(self, start_time):
        date_time_obj = time(int(start_time[0:2]),int(start_time[3:5]))
        non_peak_time_1 = time(6,0)
        non_peak_time_2 = time(18,0)
        return non_peak_time_1 <= date_time_obj <= non_peak_time_2

    def peak_period(self, start_time,initial_state, final_state, capacity,power):
        given_time = int(start_time[0:2])*60 +  int(start_time[3:5])
        expected_period = self.time_calculation(initial_state,final_state,capacity,power) * 60
        expected_end = given_time + expected_period
        hour = int(expected_end // 60)
        minute = int(expected_end % 60)
        end_time = time(hour,minute)
        if end_time <= time(18,0):
            return 100
        else :
            time_diff = expected_end - 18*60
            return int((expected_period - time_diff)*100/expected_period)

    def get_duration(self, start_time):
        pass

    # to be acquired through API
    def get_sun_hour(self, sun_hour):
        return self.weather_data['sunHours']

    # to be acquired through API
    def get_solar_energy_duration(self, start_time):
        pass

    # to be acquired through API
    def get_day_light_length(self, start_time):
        pass

    # to be acquired through API
    def get_solar_insolation(self, solar_insolation):
        pass

    # to be acquired through API
    def get_cloud_cover(self):
        pass

    def calculate_solar_energy(self):
        pass


    # Additional new function
    def get_power(self,charger_configuration):
        charger_configuration = int(charger_configuration)
        if charger_configuration == 1:
            return 2.0
        elif charger_configuration == 2:
            return 3.6
        elif charger_configuration == 3:
            return 7.2
        elif charger_configuration == 4:
            return 11
        elif charger_configuration == 5:
            return 22
        elif charger_configuration == 6:
            return 36
        elif charger_configuration == 7:
            return 90
        elif charger_configuration == 8:
            return 350
        else :
            raise Exception("NO SUCH CONFIGURATION")

    def get_price(self,charger_configuration):
        charger_configuration = int(charger_configuration)
        if charger_configuration == 1:
            return 5.0
        elif charger_configuration == 2:
            return 7.5
        elif charger_configuration == 3:
            return 10
        elif charger_configuration == 4:
            return 12.5
        elif charger_configuration == 5:
            return 15
        elif charger_configuration == 6:
            return 20
        elif charger_configuration == 7:
            return 30
        elif charger_configuration == 8:
            return 50
        else :
            raise Exception("NO SUCH CONFIGURATION")


