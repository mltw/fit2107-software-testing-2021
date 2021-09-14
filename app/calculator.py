import holidays
import datetime
import requests
import json
from datetime import time
class Calculator():
    # you can choose to initialise variables here, if needed.
    def __init__(self):
        pass

    # you may add more parameters if needed, you may modify the formula also.
    def cost_calculation(self, initial_state, final_state, capacity, is_peak, is_holiday):
        if is_peak:
            base_price = 7.5
        else:
            base_price = 7.5*0.5

        if is_holiday:
            surcharge_factor = 1.1
        else:
            surcharge_factor = 1

        cost = (final_state - initial_state) / 100 * capacity * base_price / 100 * surcharge_factor
        return cost

    # you may add more parameters if needed, you may also modify the formula.
    def time_calculation(self, initial_state, final_state, capacity, power):
        time = (final_state - initial_state) / 100 * capacity / power
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

    def peak_period(self, start_time):
        pass

    def get_duration(self, start_time):
        pass

    def get_postcode_id(self,postcode):
        link = "http://118.138.246.158/api/v1/location"
        postcode = str(postcode)
        PARAMS = {'postcode':postcode}
        r = requests.get(url=link,params=PARAMS)
        data = r.json()
        return data[0]['id']

    def get_weather_data(self,postcode,date):
        link = "http://118.138.246.158/api/v1/weather"
        id = self.get_postcode_id(postcode)
        date_time_obj = datetime.datetime.strptime(date, '%d/%m/%Y')
        new_date = str(date_time_obj.year) +  "-" + str(date_time_obj.month) + "-" + str(date_time_obj.day)
        PARAMS = {'location' : id, 'date': new_date}
        r = requests.get(url=link,params=PARAMS)
        data = r.json()
        return data

    # to be acquired through API
    def get_sun_hour(self, sun_hour):
        pass

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


