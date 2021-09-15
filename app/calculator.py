import holidays
import datetime
import requests
import json
from datetime import time, datetime
class Calculator():
    # you can choose to initialise variables here, if needed.

    def __init__(self, postcode, date):
        location_link = "http://118.138.246.158/api/v1/location"
        postcode = str(postcode)
        postcode_PARAMS = {'postcode':postcode}
        location_r = requests.get(url=location_link,params=postcode_PARAMS)
        self.location_data = location_r.json()

        self.weather_link = "http://118.138.246.158/api/v1/weather"
        self.location_id = self.location_data[0]['id']
        date_time_obj = datetime.strptime(date, '%d/%m/%Y')
        month = str(date_time_obj.month)
        if len(month) != 2 :
            month = "0" + month
        day = str(date_time_obj.day)
        if len(day)!=2:
            day = "0" + day
        new_date = "2020" + "-" + "02" + "-" + "22"
        # new_date = str(date_time_obj.year) + "-" + month + day
        self.weather_PARAMS = {'location' : self.location_id, 'date': new_date}
        self.weather_r = requests.get(url=self.weather_link,params=self.weather_PARAMS)
        self.weather_data = self.weather_r.json()

        # a_date = datetime.date(2015, 10, 10)
        # days = datetime.timedelta(5


        # print(self.weather_data)

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
        date_time_obj = datetime.strptime(start_date, '%d/%m/%Y')
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
        new_start_time = int(start_time[0:2]) * 60 + int(start_time[3:5])
        total_peak_time = 0
        if(self.is_peak(start_time)):
            if expected_end <= 18*60:
                return 100
            else :
                time_diff = expected_end - 18*60
                total_peak_time = expected_period - time_diff
        else :
            if new_start_time < 6*60:
                if expected_end < 6*60 :
                    return 0
                elif expected_end > 18*60:
                    total_peak_time = 12*60
                elif expected_end <= 18*60:
                    total_peak_time = expected_end - 6*60
                else :
                    raise Exception("the expected in not peak before 6am is wrong")
            elif new_start_time > 18*60:
                if expected_end > 18*60 :
                    total_peak_time = 0
                else:
                    raise Exception("the expected is wrong, it cannot be less than the start_time")

        if expected_end > 24*60 :
            expected_end -= 24*60
            while expected_end > 24*60 :
                total_peak_time += 12*60
                expected_end -= 24*60

            hour = int(expected_end // 60)
            minute = int(expected_end % 60)
            end_time = time(hour,minute)
            if not end_time < time(6,0) :
                if end_time > time(18,0):
                    total_peak_time += 12*60
                else:
                    total_peak_time+= expected_end - 6*60
        return int(total_peak_time*100/expected_period)

    # def get_duration(self, start_time, initial_state, final_state, capacity, power):
    #     time_needed = self.time_calculation(initial_state, final_state, capacity, power)


    # to be acquired through API
    def get_sun_hour(self):
        self.sun_hour = self.weather_data['sunHours']
        return self.sun_hour

    # to be acquired through API
    def get_solar_energy_duration(self, start_time):
        (sr,ss) = self.get_day_light_length(start_time)
        si = self.get_sun_hour()
        sunrise_hour = int(sr[0:2])
        sunrise_minute = int(sr[3:5])

        sunset_hour = int(ss[0:2])
        sunset_minute = int(ss[3:5])

        start_time_hour = int(start_time[0:2])
        start_time_minute = int(start_time[3:5])
        # self.time_calculation()
        dl =  sunset_hour+(sunset_minute/60) - sunrise_hour+(sunrise_minute/60)
        pass

    # to be acquired through API
    def get_day_light_length(self, start_time):
        self.sunrise_time = self.weather_data['sunrise']
        self.sunset_time = self.weather_data['sunset']
        return (self.sunrise_time,self.sunset_time)

    # # to be acquired through API
    # def get_solar_insolation(self, solar_insolation):
    #     pass

    # to be acquired through API
    def get_cloud_cover(self, start_date, start_time, end_date, end_time):
        # per hour basis
        start_time_hour = int(start_time[0:2])
        end_time_hour = int(end_time[0:2])

        # only for case when charging hour spans through midnight, ie 23:xx to 00:xx,
        # since this method is just to calculate each hour's cloud coverage
        if start_date != end_date:
            self.weather_link = "http://118.138.246.158/api/v1/weather"
            self.location_id = self.location_data[0]['id']

            year = str(start_date)[6:10]
            month = str(start_date)[3:5]
            day = str(start_date)[0:2]
            date_1 = year + "-" + month + "-" + day
            self.weather_PARAMS = {'location': self.location_id, 'date': date_1}
            self.weather_r = requests.get(url=self.weather_link, params=self.weather_PARAMS)
            self.weather_data = self.weather_r.json()
            print(self.weather_data)

            cc_1 = self.weather_data["hourlyWeatherHistory"][start_time_hour]["cloudCoverPct"]

            year = str(end_date)[6:10]
            month = str(end_date)[3:5]
            day = str(end_date)[0:2]
            date_2 = year + "-" + month + "-" + day
            self.weather_PARAMS = {'location': self.location_id, 'date': date_2}
            self.weather_r = requests.get(url=self.weather_link, params=self.weather_PARAMS)
            self.weather_data = self.weather_r.json()
            print(self.weather_data)

            cc_2 = self.weather_data["hourlyWeatherHistory"][end_time_hour]["cloudCoverPct"]

            return cc_1 + cc_2
        else:
            if end_time_hour > start_time_hour:
                cc_1 = self.weather_data["hourlyWeatherHistory"][start_time_hour]["cloudCoverPct"]
                cc_2 = self.weather_data["hourlyWeatherHistory"][end_time_hour]["cloudCoverPct"]
                return int(cc_1)+int(cc_2)
            elif end_time_hour < start_time_hour:
                raise ValueError("End time cannot be lesser than start time")
            else:
                return self.weather_data["hourlyWeatherHistory"][start_time_hour]["cloudCoverPct"]

        # time_needed = self.time_calculation(initial_state, final_state, capacity, power)
        #
        # date_time_obj = datetime.strptime(start_date, '%d/%m/%Y')
        #
        # date_time_str = str(date_time_obj) + " " +  str(start_time)
        # date_time_obj = datetime.strptime(date_time_str, '%d/%m/%Y %H:%M')
        # date_time_after_charge = date_time_obj + datetime.timedelta(hours=time_needed)


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


