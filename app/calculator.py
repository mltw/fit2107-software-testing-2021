import holidays
import datetime
import requests
import json
from datetime import time, datetime,timedelta
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
    def cost_calculation(self, initial_state, final_state, capacity, peak_period, holiday_percent,base_price):
        assert peak_period >= 0 and peak_period <= 1 , "Please provide a valid peak_period, must be between 0 and 100"
        assert holiday_percent >= 0 and holiday_percent <= 1 , "Please provide a valid holiday_percent, must be between 0 and 100"
        non_peak = 0.5*(1-(peak_period))
        peak = (1*(peak_period))
        # print("original Base price : ", base_price)
        base_price =base_price*(non_peak+peak)
        # print("base price : ", base_price)

        surcharge_factor =  1.1*holiday_percent + 1*(1-holiday_percent)
        # print("surcharge_factor : ",surcharge_factor)

        cost = (int(final_state) - int(initial_state)) / 100 * int(capacity) * base_price / 100 * surcharge_factor
        return cost

    # you may add more parameters if needed, you may also modify the formula.
    def time_calculation(self, initial_state, final_state, capacity, power):
        time = (int(final_state) - int(initial_state)) / 100 * int(capacity) / power
        return round(time,2)


    # you may create some new methods at your convenience, or modify these methods, or choose not to use them.
    def is_holiday(self, start_date):
        aus_holidays = holidays.Australia()
        date_time_obj = datetime.strptime(start_date, '%d/%m/%Y')
        return date_time_obj in aus_holidays or date_time_obj.weekday() <= 4

    def is_holiday_temp_2(self, start_date):
        aus_holidays = holidays.Australia()
        return start_date in aus_holidays or start_date.weekday() <= 4

    def is_holiday_temp(self, start_date,initial_state, final_state, capacity, power,start_time):
        time = self.time_calculation(initial_state, final_state, capacity, power)

        time_array = start_time.split(':')
        st_hour = int(time_array[0])
        st_minute = int(time_array[1])
        new_start_date = datetime.strptime(start_date, '%d/%m/%Y')

        num_of_day = time//24
        remaining_time = round(time%24,2)

        expected_end_time = st_hour*60 + st_minute + time*60
        # If it does not exceed first day
        if (st_hour*60 + st_minute) + time*60 <= 24*60 :
            # if holiday return 100%, it means 100% holiday
            if self.is_holiday_temp_2(new_start_date):
                return 1
            # else 0% holiday
            else :
                return 0
        # if it exceed first day, more than 1 day
        else :
            # if first day is holiday, add it into holiday_minute_total
            if self.is_holiday_temp_2(new_start_date):
                holiday_minute_total = 24*60 - st_hour*60 - st_minute
            else :
                holiday_minute_total = 0
            next_date = new_start_date + timedelta(hours=24)
            expected_end_time -= 24*60
            while expected_end_time >= 24*60:
                expected_end_time -= 24*60
                if self.is_holiday_temp_2(next_date) :
                    holiday_minute_total += 24*60
                next_date += timedelta(hours=24)
            # last day
            if self.is_holiday_temp_2(next_date):
                holiday_minute_total += expected_end_time
            return round(holiday_minute_total/(time*60),4)

    def is_peak(self, start_time):
        time_array = start_time.split(':')
        st_hour = int(time_array[0])
        st_minute = int(time_array[1])
        date_time_obj = time(int(st_hour),int(st_minute))
        non_peak_time_1 = time(6,0)
        non_peak_time_2 = time(18,0)
        return non_peak_time_1 <= date_time_obj <= non_peak_time_2

    def peak_period(self, start_time,initial_state, final_state, capacity,power):
        time_array = start_time.split(':')
        st_hour = int(time_array[0])
        st_minute = int(time_array[1])
        given_time = int(st_hour)*60 +  int(st_minute)
        expected_period = self.time_calculation(initial_state,final_state,capacity,power) * 60
        expected_end = given_time + expected_period
        new_start_time = int(st_hour) * 60 + int(st_minute)
        total_peak_time = 0
        if(self.is_peak(start_time)):
            if expected_end <= 18*60:
                return 1
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
                    total_peak_time += expected_end - 6*60
        return round(total_peak_time/expected_period,4)

    # def get_duration(self, start_time, initial_state, final_state, capacity, power):
    #     time_needed = self.time_calculation(initial_state, final_state, capacity, power)


    # to be acquired through API
    def get_sun_hour(self, start_date):
        self.weather_link = "http://118.138.246.158/api/v1/weather"
        self.location_id = self.location_data[0]['id']

        year = str(start_date)[6:10]
        month = str(start_date)[3:5]
        day = str(start_date)[0:2]
        date_1 = year + "-" + month + "-" + day
        self.weather_PARAMS = {'location': self.location_id, 'date': date_1}
        self.weather_r = requests.get(url=self.weather_link, params=self.weather_PARAMS)
        self.weather_data = self.weather_r.json()

        self.sun_hour = self.weather_data['sunHours']
        return self.sun_hour

    # to be acquired through API
    def get_solar_energy_duration(self, start_time):
        # (sr,ss) = self.get_day_light_length(start_time)
        # si = self.get_sun_hour()
        # sunrise_hour = int(sr[0:2])
        # sunrise_minute = int(sr[3:5])
        #
        # sunset_hour = int(ss[0:2])
        # sunset_minute = int(ss[3:5])
        #
        # start_time_hour = int(start_time[0:2])
        # start_time_minute = int(start_time[3:5])
        # # self.time_calculation()
        # dl =  sunset_hour+(sunset_minute/60) - sunrise_hour+(sunrise_minute/60)
        pass

    # to be acquired through API
    def get_day_light_length(self, start_date):
        # Meng Yew approved this
        # per day basis
        self.weather_link = "http://118.138.246.158/api/v1/weather"
        self.location_id = self.location_data[0]['id']

        date = start_date.split('/')
        year = date[2]
        month = date[1]
        day = date[0]
        date_1 = year + "-" + month + "-" + day
        self.weather_PARAMS = {'location': self.location_id, 'date': date_1}
        self.weather_r = requests.get(url=self.weather_link, params=self.weather_PARAMS)
        self.weather_data = self.weather_r.json()
        # sunrise_time_format : 05:10:00
        # sunset_time_format : 19:24:00
        sunrise_time = self.weather_data['sunrise']
        sunset_time = self.weather_data['sunset']

        # sunrise_time_format : [hour,minute,seconds]
        # sunrise_time_format : [5,10,0]
        # sunset_time_format : [19,24,0]
        sunrise_time = sunrise_time.split(':')
        sunset_time  = sunset_time.split(':')

        sunrise_hour = int(sunrise_time[0])
        sunrise_minute = int(sunrise_time[1])

        sunset_hour = int(sunset_time[0])
        sunset_minute = int(sunset_time[1])

        if sunset_minute < sunrise_minute:
            sunset_minute += 60
            sunset_hour -= 1

        return (sunset_hour - sunrise_hour) + (sunset_minute - sunrise_minute)/60

        # return (self.sunrise_time,self.sunset_time)

    # # to be acquired through API
    # def get_solar_insolation(self, solar_insolation):
    #     pass

    # to be acquired through API
    def get_cloud_cover(self, start_date, start_time, end_date, end_time):
        # per hour basis
        # start time format 03:22 -> [3,22]
        start_time = start_time.split(':')
        start_time_hour = int(start_time[0])
        start_time_minute = int(start_time[1])

        # end time format 03:22 -> [3,22]
        end_time = end_time.split(':')
        end_time_hour = int(end_time[0])
        end_time_minute = int(end_time[1])

        start_date_time_obj = datetime.strptime(start_date, '%d/%m/%Y')
        end_date_time_obj = datetime.strptime(end_date, '%d/%m/%Y')

        if end_date_time_obj < start_date_time_obj:
            raise ValueError("End date cannot be earlier than start date")
        # only for case when charging hour spans through midnight, ie 23:xx to 00:xx,
        # since this method is just to calculate each hour's cloud coverage
        elif start_date != end_date:
            # retrieve from API respective date's cloud coverage
            self.weather_link = "http://118.138.246.158/api/v1/weather"
            self.location_id = self.location_data[0]['id']

            temp_start_date = str(start_date).split('/')
            year = temp_start_date[2]
            month = temp_start_date[1]
            day = temp_start_date[0]
            date_1 = year + "-" + month + "-" + day
            self.weather_PARAMS = {'location': self.location_id, 'date': date_1}
            self.weather_r = requests.get(url=self.weather_link, params=self.weather_PARAMS)
            self.weather_data = self.weather_r.json()
            # print(self.weather_data)

            cc_1 = self.weather_data["hourlyWeatherHistory"][start_time_hour]["cloudCoverPct"]

            temp_end_date = str(start_date).split('/')
            year = temp_end_date[2]
            month = temp_end_date[1]
            day = temp_end_date[0]
            date_2 = year + "-" + month + "-" + day
            self.weather_PARAMS = {'location': self.location_id, 'date': date_2}
            self.weather_r = requests.get(url=self.weather_link, params=self.weather_PARAMS)
            self.weather_data = self.weather_r.json()
            # print(self.weather_data)

            cc_2 = self.weather_data["hourlyWeatherHistory"][end_time_hour]["cloudCoverPct"]
            print(cc_1,cc_2)

            return cc_1 + cc_2
        else:
            if end_time_hour > start_time_hour:
                cc_1 = self.weather_data["hourlyWeatherHistory"][start_time_hour]["cloudCoverPct"]
                cc_2 = self.weather_data["hourlyWeatherHistory"][end_time_hour]["cloudCoverPct"]
                return int(cc_1)+int(cc_2)
            elif end_time_hour < start_time_hour:
                raise ValueError("End time cannot be lesser than start time")
            elif end_time_minute < start_time_minute:
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

    def get_duration(self, start_time, end_time):
        # start and end time are of type integer, eg 730, 1640, 20
        start_time_hour = 0
        if len(start_time) == 1 or len(start_time) == 2:
            start_time_minute = start_time
        elif len(start_time) == 3:
            start_time_minute = start_time[-2:]
            start_time_hour = start_time[0]
        else:
            start_time_minute = start_time[-2:]
            start_time_hour = start_time[0:2]

        end_time_hour = start_time_hour
        if len(end_time) == 1 or len(end_time) == 2:
            end_time_minute = start_time
        elif len(end_time) == 3:
            end_time_minute = end_time[-2:]
            end_time_hour = end_time[0]
        else:
            end_time_minute = end_time[-2:]
            end_time_hour = end_time[0:2]

        start_time_hour = int(start_time_hour)
        start_time_minute = int(start_time_minute)
        end_time_hour = int(end_time_hour)
        end_time_minute = int(end_time_minute)

        if end_time_minute < start_time_minute:
            end_time_minute += 60
            end_time_hour -= 1

        du_minute = end_time_minute - start_time_minute
        du_hour = end_time_hour - start_time_hour
        return int(str(du_hour)+str(du_minute))

    def calculate_solar_energy_within_a_day(self, start_date, start_time, end_time):
        # get solar hour/insolation (si) and daylight length (dl)
        si = self.get_sun_hour(start_date)
        dl = self.get_day_light_length(start_date)

        # get sunrise and sunset time
        self.weather_link = "http://118.138.246.158/api/v1/weather"
        self.location_id = self.location_data[0]['id']

        year = str(start_date)[6:10]
        month = str(start_date)[3:5]
        day = str(start_date)[0:2]
        date_1 = year + "-" + month + "-" + day
        self.weather_PARAMS = {'location': self.location_id, 'date': date_1}
        self.weather_r = requests.get(url=self.weather_link, params=self.weather_PARAMS)
        self.weather_data = self.weather_r.json()

        sr = self.weather_data['sunrise']
        ss = self.weather_data['sunset']

        # parse to appropriate format
        sr = int(str(sr[0:2]) + str(sr[3:5]))
        ss = int(str(ss[0:2]) + str(ss[3:5]))
        start_time = int(str(start_time[0:2]) + str(start_time[3:5]))
        # print(start_time)
        # print(end_time)
        end_time = int(str(end_time[0:2]) + str(end_time[3:5]))

        if ss >= start_time >= sr:
            if end_time >= ss:
                du = self.get_duration(str(start_time), str(ss))
            else:
                du = self.get_duration(str(start_time), str(end_time))

        elif start_time < sr:
            if ss >= end_time >= sr:
                du = self.get_duration(str(sr), str(end_time))
            elif end_time > ss:
                du = self.get_duration(str(sr), str(ss))
            else:
                du = 0
        else: # = elif start_time > ss
            du = 0

        if len(str(du)) == 1 or len(str(du)) == 2:
            final_du = du / 60 # convert to hours
        elif len(str(du)) == 3:
            final_du = int(str(du)[0]) + int(str(du)[1:3]) / 60
        else:
            final_du = int(str(du)[0:2]) + int(str(du)[2:4]) / 60
        return si * final_du / dl * 50 * 0.2

    def calculate_solar_energy(self, start_date, start_time, initial_state, final_state, capacity, power):
        charge_time = self.time_calculation(initial_state, final_state, capacity, power)
        start_time_hour = int(start_time[0:2])
        start_time_minute = int(start_time[3:5])

        # start_time_in_hours = start_time_hour + start_time_minute/60

        charge_time_hour = charge_time * 60 // 60
        charge_time_minute = charge_time * 60 % 60

        end_time_hour = start_time_hour + charge_time_hour
        end_time_minute = start_time_minute + charge_time_minute

        start_time_obj = datetime.strptime( start_time, '%H:%M')
        end_time_obj = start_time_obj + timedelta(hours=charge_time_hour, minutes=charge_time_minute)

        # print('eth: ' + str(end_time_hour))
        # print('etm: ' + str(end_time_minute))
        # print('cth: ' + str(charge_time_hour))
        # print('ctm: ' + str(charge_time_minute))
        # print('eto: ' + str(end_time_obj))

        # if end_time_minute >= 60:
        #     end_time_minute -= 60
        #     end_time_hour += 1
        # end_time = str(end_time_hour) + ":" + str(end_time_minute)
        end_time = str(end_time_obj.time())[0:5]

        # within a single day
        if end_time_hour + end_time_minute/60 <= 23.59:
            res = self.calculate_solar_energy_within_a_day(start_date, start_time, end_time)
        else:
            res = 0
            date_time_obj = datetime.strptime(start_date + " " + start_time, '%d/%m/%Y %H:%M')
            date_time_after_charge = date_time_obj + timedelta(hours=charge_time)
            start_time_new = start_time
            charge_date_new = str(date_time_obj.date())[8:10] \
                              + "/" + str(date_time_obj.date())[5:7] \
                              + "/" + str(date_time_obj.date())[0:4]

            while date_time_obj.day != date_time_after_charge.day:
                charge_date_new = str(date_time_obj.date())[8:10] \
                                  + "/" + str(date_time_obj.date())[5:7] \
                                  + "/" + str(date_time_obj.date())[0:4]
                # temp_duration = timedelta(hours=24) - timedelta(hours=start_time_hour, minutes=start_time_minute)

                res += self.calculate_solar_energy_within_a_day(charge_date_new, start_time_new, "23:59")
                date_time_obj += timedelta(days=1)
                start_time_new = "00:00"

            res += self.calculate_solar_energy_within_a_day(charge_date_new, start_time_new, end_time)

        return res

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


# date_time_obj = datetime.strptime("28/02/2021" + " " + "22:02", '%d/%m/%Y %H:%M')
# # date_time_str = str(date_time_obj) + " " + str(start_time)
# # date_time_obj = datetime.strptime(date_time_str, '%d/%m/%Y %H:%M')
# date_time_after_charge = date_time_obj + timedelta(hours=3)
# print(date_time_after_charge.day)
# print(date_time_obj + timedelta(days = 1))
# temp_du = timedelta(hours=24) - timedelta(hours=5, minutes=55)
# print(temp_du)
# print(date_time_obj.date())
#
# location_link = "http://118.138.246.158/api/v1/location"
# postcode = str(6000)
# postcode_PARAMS = {'postcode': postcode}
# location_r = requests.get(url=location_link, params=postcode_PARAMS)
# location_data = location_r.json()
#
# weather_link = "http://118.138.246.158/api/v1/weather"
# location_id = location_data[0]['id']
# date_time_obj = datetime.strptime("25/12/2020", '%d/%m/%Y')
# month = str(date_time_obj.month)
# if len(month) != 2:
#     month = "0" + month
# day = str(date_time_obj.day)
# if len(day) != 2:
#     day = "0" + day
# new_date = "2020" + "-" + "02" + "-" + "22"
# # new_date = str(date_time_obj.year) + "-" + month + day
# weather_PARAMS = {'location': location_id, 'date': new_date}
# weather_r = requests.get(url=weather_link, params=weather_PARAMS)
# weather_data = weather_r.json()