import holidays
import datetime
import requests
import json
from datetime import time, datetime,timedelta
from dateutil.relativedelta import relativedelta

class Calculator():
    # you can choose to initialise variables here, if needed.

    def __init__(self, postcode, date, location_name=""):
        location_link = "http://118.138.246.158/api/v1/location"
        postcode = str(postcode)
        postcode_PARAMS = {'postcode':postcode}
        location_r = requests.get(url=location_link,params=postcode_PARAMS)
        self.location_data = location_r.json()
        # print(self.location_data)

        self.weather_link = "http://118.138.246.158/api/v1/weather"
        self.location_id = -1
        # find the correct location's id
        for i in range(len(self.location_data)):
            # print(self.location_data[i]["name"].lower())
            # print(self.location_data[i]["name"].lower() == location_name.lower())
            if self.location_data[i]["name"].lower() == location_name.lower():
                self.location_id = self.location_data[i]['id']
                break
            else:
                pass
        # if the user input location name is invalid, just take the first location
        if self.location_id == -1:
            self.location_id = self.location_data[0]['id']
        # print(self.location_id)
        # ----------------------------------
        max_date_allowed = datetime.now() - timedelta(days=2)

        current_date = datetime.strptime(date, '%d/%m/%Y')

        # since the API can only handle dates up to current date - 2 days, get the closest reference date first
        if current_date <= max_date_allowed:
            date_time_obj = current_date
        else:
            ref_date_per_year = current_date
            # future, so find reference dates
            while ref_date_per_year.year != datetime.now().year:
                ref_date_per_year -= relativedelta(years=1)

            if ref_date_per_year <= current_date:
                date_time_obj = ref_date_per_year
            else:
                date_time_obj = ref_date_per_year - relativedelta(years=1)
        # ----------------------------------

        # date_time_obj = datetime.strptime(date, '%d/%m/%Y')
        month = str(date_time_obj.month)
        if len(month) != 2 :
            month = "0" + month
        day = str(date_time_obj.day)
        if len(day)!=2:
            day = "0" + day
        # new_date = "2020" + "-" + "02" + "-" + "22"
        new_date = str(date_time_obj.year) + "-" + month + "-" + day
        # print("new_date", new_date)
        self.weather_PARAMS = {'location': self.location_id, 'date': new_date}
        self.weather_r = requests.get(url=self.weather_link, params=self.weather_PARAMS)
        self.weather_data = self.weather_r.json()
        # print('new', self.weather_data)

    # you may add more parameters if needed, you may modify the formula also.
    def cost_calculation_v2(self, initial_state, final_state, capacity,base_price,power,start_date,start_time):
        # requirement 2 can't take in future dates, so just return a '-'
        max_date_allowed = datetime.now() - timedelta(days=2)

        current_date = datetime.strptime(start_date, '%d/%m/%Y')

        if current_date <= max_date_allowed:
            pass
        else:
            return '-'
        power_list = self.calculate_solar_energy_new(start_date, start_time, initial_state, final_state,capacity, power)
        print('v2', power_list)
        date = start_date.split('/')
        time = start_time.split(':')
        current_datetime = datetime(int(date[2]),int(date[1]),int(date[0]),int(time[0]),int(time[1]))

        base_price =base_price
        surcharge_factor =  1.1
        total_time = self.time_calculation(initial_state, final_state, capacity,power)
        total_cost = 0

        first_hour_datetime = datetime(int(date[2]),int(date[1]),int(date[0]),int(time[0]),0) + timedelta(hours=1)
        time_difference = first_hour_datetime - current_datetime
        minute_difference = time_difference.total_seconds()/60
        hour_difference = minute_difference/60
        # calculate the cost for the first hour
        # if the first hour contains all the time
        if total_time <= hour_difference :
            price = base_price*0.5 if not self.is_peak_v2(current_datetime) else base_price
            surcharge = surcharge_factor if self.is_holiday_v2(current_datetime) else 1
            extra_power = power_list[0][2]
            total_power = max((((float(final_state) - float(initial_state)) / 100) * float(capacity)) - extra_power,0)
            total_cost = total_power * price / 100 * surcharge
            return total_cost
        else :
            price = base_price*0.5 if not self.is_peak_v2(current_datetime) else base_price
            surcharge = surcharge_factor if self.is_holiday_v2(current_datetime) else 1
            partial_initial_state = float(initial_state)
            partial_final_state = partial_initial_state + ((float(final_state) - float(initial_state))/total_time) * hour_difference
            extra_power = power_list[0][2]
            total_power = max(((partial_final_state-partial_initial_state)/100) * float(capacity)-extra_power,0)
            total_cost += total_power* price / 100 * surcharge
            # print("tc 1 :" ,total_cost,partial_initial_state,partial_final_state,total_time)
            current_datetime = first_hour_datetime
            temp_total_time = total_time - hour_difference
            current_power = 1
            while temp_total_time >= 1 :
                temp_total_time -= 1
                current_datetime += timedelta(minutes=30)
                price = base_price*0.5 if not self.is_peak_v2(current_datetime) else base_price
                surcharge = surcharge_factor if self.is_holiday_v2(current_datetime) else 1
                partial_initial_state = partial_final_state
                partial_final_state += ((float(final_state) - float(initial_state))/total_time)
                # use
                extra_power= power_list[current_power][2]
                total_power = max(((partial_final_state-partial_initial_state)/100) * float(capacity)-extra_power,0)
                total_cost += total_power* price / 100 * surcharge
                current_datetime += timedelta(minutes=30)
                current_power += 1
            # print("tc 2 : ",total_cost,partial_initial_state,partial_final_state)
            if temp_total_time > 0 :
                total_minute = round(temp_total_time*60,0)
                current_datetime += timedelta(minutes=total_minute)
                price = base_price*0.5 if not self.is_peak_v2(current_datetime) else base_price
                surcharge = surcharge_factor if self.is_holiday_v2(current_datetime) else 1
                partial_initial_state = partial_final_state
                partial_final_state = float(final_state)
                extra_power= power_list[current_power][2]
                total_power = max(((partial_final_state-partial_initial_state)/100)* float(capacity) - extra_power,0)
                total_cost += total_power* price / 100 * surcharge
            return round(total_cost,2)

    # for requirement 3
    def cost_calculation_v3(self, initial_state, final_state, capacity, base_price, power, start_date, start_time):
        power_list = self.calculate_solar_energy_new_w_cc(start_date, start_time, initial_state, final_state,capacity, power)
        print(power_list)
        date = start_date.split('/')
        time = start_time.split(':')
        current_datetime = datetime(int(date[2]),int(date[1]),int(date[0]),int(time[0]),int(time[1]))

        base_price = base_price
        surcharge_factor = 1.1
        total_time = self.time_calculation(initial_state, final_state, capacity,power)
        total_cost = 0

        first_hour_datetime = datetime(int(date[2]),int(date[1]),int(date[0]),int(time[0]),0) + timedelta(hours=1)
        time_difference = first_hour_datetime - current_datetime
        minute_difference = time_difference.total_seconds()/60
        hour_difference = minute_difference/60
        # calculate the cost for the first hour
        # if the first hour contains all the time
        for i in range(len(power_list)):
            if total_time <= hour_difference:
                price = base_price*0.5 if not self.is_peak_v2(current_datetime) else base_price
                surcharge = surcharge_factor if self.is_holiday_v2(current_datetime) else 1
                extra_power = power_list[i][0][2]
                total_power = max((((float(final_state) - float(initial_state)) / 100) * float(capacity)) - extra_power,0)
                total_cost = total_power * price / 100 * surcharge
                return total_cost
            else :
                price = base_price*0.5 if not self.is_peak_v2(current_datetime) else base_price
                surcharge = surcharge_factor if self.is_holiday_v2(current_datetime) else 1
                partial_initial_state = float(initial_state)
                partial_final_state = partial_initial_state + ((float(final_state) - float(initial_state))/total_time) * hour_difference
                extra_power = power_list[i][0][2]
                total_power = max(((partial_final_state-partial_initial_state)/100) * float(capacity)-extra_power,0)
                total_cost += total_power* price / 100 * surcharge
                # print("tc 1 :" ,total_cost,partial_initial_state,partial_final_state,total_time)
                current_datetime = first_hour_datetime
                temp_total_time = total_time - hour_difference
                current_power = 1
                while temp_total_time >= 1 :
                    temp_total_time -= 1
                    current_datetime += timedelta(minutes=30)
                    price = base_price*0.5 if not self.is_peak_v2(current_datetime) else base_price
                    surcharge = surcharge_factor if self.is_holiday_v2(current_datetime) else 1
                    partial_initial_state = partial_final_state
                    partial_final_state += ((float(final_state) - float(initial_state))/total_time)
                    # use
                    extra_power= power_list[i][current_power][2]
                    total_power = max(((partial_final_state-partial_initial_state)/100) * float(capacity)-extra_power,0)
                    total_cost += total_power* price / 100 * surcharge
                    current_datetime += timedelta(minutes=30)
                    current_power += 1
                # print("tc 2 : ",total_cost,partial_initial_state,partial_final_state)
                if temp_total_time > 0 :
                    total_minute = round(temp_total_time*60,0)
                    current_datetime += timedelta(minutes=total_minute)
                    price = base_price*0.5 if not self.is_peak_v2(current_datetime) else base_price
                    surcharge = surcharge_factor if self.is_holiday_v2(current_datetime) else 1
                    partial_initial_state = partial_final_state
                    partial_final_state = float(final_state)
                    extra_power= power_list[i][current_power][2]
                    total_power = max(((partial_final_state-partial_initial_state)/100)* float(capacity) - extra_power,0)
                    total_cost += total_power* price / 100 * surcharge
                return round(total_cost/len(power_list),2)

    # you may add more parameters if needed, you may also modify the formula.
    def time_calculation(self, initial_state, final_state, capacity, power):
        time = (float(final_state) - float(initial_state)) / 100 * float(capacity) / power
        return round(time,2)


    # you may create some new methods at your convenience, or modify these methods, or choose not to use them.
    def is_holiday_v2(self, start_date):
        aus_holidays = holidays.Australia()
        return start_date in aus_holidays or start_date.weekday() <= 4

    def is_peak_v2(self,start_time):
        non_peak_time_1 = datetime(start_time.year,start_time.month,start_time.day,6,0,0)
        non_peak_time_2 = datetime(start_time.year,start_time.month,start_time.day,18,0,0)
        return non_peak_time_1 <= start_time <= non_peak_time_2

    # def get_duration(self, start_time, initial_state, final_state, capacity, power):
    #     time_needed = self.time_calculation(initial_state, final_state, capacity, power)


    # to be acquired through API
    def get_sun_hour(self, start_date):
        self.weather_link = "http://118.138.246.158/api/v1/weather"
        # self.location_id = self.location_data[0]['id']

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
        # self.location_id = self.location_data[0]['id']

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
    # def get_cloud_cover(self, start_date, start_time, end_date, end_time):
    #     # per hour basis
    #     # start time format 03:22 -> [3,22]
    #     start_time = start_time.split(':')
    #     start_time_hour = int(start_time[0])
    #     start_time_minute = int(start_time[1])
    #
    #     # end time format 03:22 -> [3,22]
    #     end_time = end_time.split(':')
    #     end_time_hour = int(end_time[0])
    #     end_time_minute = int(end_time[1])
    #
    #     start_date_time_obj = datetime.strptime(start_date, '%d/%m/%Y')
    #     end_date_time_obj = datetime.strptime(end_date, '%d/%m/%Y')
    #
    #     if end_date_time_obj < start_date_time_obj:
    #         raise ValueError("End date cannot be earlier than start date")
    #     # only for case when charging hour spans through midnight, ie 23:xx to 00:xx,
    #     # since this method is just to calculate each hour's cloud coverage
    #     elif start_date != end_date:
    #         # retrieve from API respective date's cloud coverage
    #         self.weather_link = "http://118.138.246.158/api/v1/weather"
    #         self.location_id = self.location_data[0]['id']
    #
    #         temp_start_date = str(start_date).split('/')
    #         year = temp_start_date[2]
    #         month = temp_start_date[1]
    #         day = temp_start_date[0]
    #         date_1 = year + "-" + month + "-" + day
    #         self.weather_PARAMS = {'location': self.location_id, 'date': date_1}
    #         self.weather_r = requests.get(url=self.weather_link, params=self.weather_PARAMS)
    #         self.weather_data = self.weather_r.json()
    #         # print(self.weather_data)
    #
    #         cc_1 = 0
    #         cc_2 = 0
    #
    #         # hourlyWeatherHistory's output of hours are not in order 0 - 23, may change sometimes,
    #         # thus need to manually loop through the whole array
    #         for i in range(24):
    #             if self.weather_data["hourlyWeatherHistory"][i]["hour"] == start_time:
    #                 cc_1 = self.weather_data["hourlyWeatherHistory"][i]["cloudCoverPct"]
    #                 break
    #             else:
    #                 pass
    #
    #         temp_end_date = str(start_date).split('/')
    #         year = temp_end_date[2]
    #         month = temp_end_date[1]
    #         day = temp_end_date[0]
    #         date_2 = year + "-" + month + "-" + day
    #         self.weather_PARAMS = {'location': self.location_id, 'date': date_2}
    #         self.weather_r = requests.get(url=self.weather_link, params=self.weather_PARAMS)
    #         self.weather_data = self.weather_r.json()
    #
    #         for i in range(24):
    #             if self.weather_data["hourlyWeatherHistory"][i]["hour"] == start_time:
    #                 cc_2 = self.weather_data["hourlyWeatherHistory"][i]["cloudCoverPct"]
    #                 break
    #             else:
    #                 pass
    #
    #         return cc_1 + cc_2
    #     else:
    #         if end_time_hour > start_time_hour:
    #             cc_1 = self.weather_data["hourlyWeatherHistory"][start_time_hour]["cloudCoverPct"]
    #             cc_2 = self.weather_data["hourlyWeatherHistory"][end_time_hour]["cloudCoverPct"]
    #             return int(cc_1)+int(cc_2)
    #         elif end_time_hour < start_time_hour:
    #             raise ValueError("End time cannot be lesser than start time")
    #         elif end_time_minute < start_time_minute:
    #             raise ValueError("End time cannot be lesser than start time")
    #         else:
    #             return self.weather_data["hourlyWeatherHistory"][start_time_hour]["cloudCoverPct"]
    #
    #     # time_needed = self.time_calculation(initial_state, final_state, capacity, power)
    #     #
    #     # date_time_obj = datetime.strptime(start_date, '%d/%m/%Y')
    #     #
    #     # date_time_str = str(date_time_obj) + " " +  str(start_time)
    #     # date_time_obj = datetime.strptime(date_time_str, '%d/%m/%Y %H:%M')
    #     # date_time_after_charge = date_time_obj + datetime.timedelta(hours=time_needed)
    def get_cloud_cover(self, start_date, start_time, end_time):
        # this method should be called within the same start and end time hour
        self.weather_link = "http://118.138.246.158/api/v1/weather"
        # self.location_id = self.location_data[0]['id']
        date_time_obj = datetime.strptime(start_date, '%d/%m/%Y')
        month = str(date_time_obj.month)
        if len(month) != 2:
            month = "0" + month
        else:
            pass

        day = str(date_time_obj.day)
        if len(day) != 2:
            day = "0" + day
        else:
            pass

        new_date = str(date_time_obj.year) + "-" + month + "-" + day
        self.weather_PARAMS = {'location': self.location_id, 'date': new_date}
        self.weather_r = requests.get(url=self.weather_link, params=self.weather_PARAMS)
        self.weather_data = self.weather_r.json()

        # per hour basis
        # start time format 03:22 -> [3,22]
        start_time = start_time.split(':')
        start_time_hour = int(start_time[0])
        # print('st', start_time)
        start_time_as_integer = int(start_time[0]+start_time[1])

        # end time format 03:22 -> [3,22]
        end_time = end_time.split(':')
        # print('et', end_time)
        end_time_as_integer = int(end_time[0] + end_time[1])

        if end_time_as_integer < start_time_as_integer:
            raise ValueError("End time cannot be earlier than start time")
        else:
            cc = 0
            # print(self.weather_data)
            for i in range(24):
                # print(i, self.weather_data["hourlyWeatherHistory"][i]["hour"], self.weather_data["hourlyWeatherHistory"][i]["cloudCoverPct"])
                if self.weather_data["hourlyWeatherHistory"][i]["hour"] == start_time_hour:
                    cc = self.weather_data["hourlyWeatherHistory"][i]["cloudCoverPct"]
                    print('cc', cc)
                    return cc
                else:
                    pass
            return cc

    def get_duration(self, start_time, end_time):
        # start and end time are time in type string, eg "730", "1640", "20"
        # it returns the duration between start_time and end_time, in hours
        # eg if start_time = "1030", end_time = "1200", it will return 1.5 (ie 1 hr 30 minutes)
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

        if len(str(du_minute)) == 1:
           du_minute = '0' + str(du_minute)
        else:
            pass
        du = int(str(du_hour)+str(du_minute))

        if len(str(du)) == 1 or len(str(du)) == 2:
            final_du = du / 60 # convert to hours
        elif len(str(du)) == 3:
            final_du = int(str(du)[0]) + int(str(du)[1:3]) / 60
        else:
            final_du = int(str(du)[0:2]) + int(str(du)[2:4]) / 60

        return final_du

    def calculate_solar_energy_within_a_day_by_hour(self, start_date, start_time, end_time):
        # get solar hour/insolation (si) and daylight length (dl)
        si = self.get_sun_hour(start_date)
        dl = self.get_day_light_length(start_date)

        # get sunrise and sunset time
        self.weather_link = "http://118.138.246.158/api/v1/weather"
        # self.location_id = self.location_data[0]['id']

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

        start_time_hour = int(str(start_time)[0:2])
        start_time = int(str(start_time[0:2]) + str(start_time[3:5]))

        end_time_hour = int(str(end_time)[0:2])
        end_time = int(str(end_time[0:2]) + str(end_time[3:5]))

        arr = []

        while start_time_hour <= end_time_hour:
            if start_time_hour == end_time_hour:
                start_time_temp = start_time
                end_time_temp = end_time
            else:
                end_time_temp_hour = start_time_hour+1
                start_time_temp = start_time
                end_time_temp = int(str(end_time_temp_hour)+"00")

            if ss >= start_time_temp >= sr:
                if end_time_temp >= ss:
                    du = self.get_duration(str(start_time_temp), str(ss))

                else:
                    du = self.get_duration(str(start_time_temp), str(end_time_temp))

            elif start_time_temp < sr:
                if ss >= end_time_temp >= sr:
                    du = self.get_duration(str(sr), str(end_time_temp))
                elif end_time_temp > ss:
                    du = self.get_duration(str(sr), str(ss))
                else:
                    du = 0
            else: # = elif start_time > ss
                du = 0

            solar_energy = si * du / dl * 50 * 0.2

            arr.append([start_time_temp, end_time_temp, solar_energy])
            start_time_hour += 1
            start_time = int(str(start_time_hour)+"00")

        return arr

    def calculate_solar_energy_new(self, start_date, start_time, initial_state, final_state,
                                   capacity, power):
        charge_time = self.time_calculation(initial_state, final_state, capacity, power)
        start_time_hour = int(start_time[0:2])
        start_time_minute = int(start_time[3:5])

        # start_time_in_hours = start_time_hour + start_time_minute/60

        charge_time_hour = charge_time * 60 // 60
        charge_time_minute = charge_time * 60 % 60

        end_time_hour = start_time_hour + charge_time_hour
        end_time_minute = start_time_minute + charge_time_minute

        start_time_obj = datetime.strptime(start_time, '%H:%M')
        end_time_obj = start_time_obj + timedelta(hours=charge_time_hour, minutes=charge_time_minute)

        end_time = str(end_time_obj.time())[0:5]

        res = []
        # within a single day
        if end_time_hour + end_time_minute / 60 <= 23.59:
            res += (self.calculate_solar_energy_within_a_day_by_hour(start_date, start_time, end_time))
        else:
            date_time_obj = datetime.strptime(start_date + " " + start_time, '%d/%m/%Y %H:%M')
            date_time_after_charge = date_time_obj + timedelta(hours=charge_time)
            start_time_new = start_time

            while date_time_obj.day != date_time_after_charge.day:
                charge_date_new = str(date_time_obj.date())[8:10] \
                                  + "/" + str(date_time_obj.date())[5:7] \
                                  + "/" + str(date_time_obj.date())[0:4]
                # temp_duration = timedelta(hours=24) - timedelta(hours=start_time_hour, minutes=start_time_minute)

                res += (self.calculate_solar_energy_within_a_day_by_hour(charge_date_new, start_time_new, "23:59"))
                date_time_obj += timedelta(days=1)
                start_time_new = "00:00"

            charge_date_new = str(date_time_obj.date())[8:10] \
                              + "/" + str(date_time_obj.date())[5:7] \
                              + "/" + str(date_time_obj.date())[0:4]
            res += self.calculate_solar_energy_within_a_day_by_hour(charge_date_new, start_time_new, end_time)

        return res

    # --------------------------------- Requirement 3 -----------------------------------
    def calculate_solar_energy_within_a_day_by_hour_w_cc(self, start_date, start_time, end_time):
        # get solar hour/insolation (si) and daylight length (dl)
        si = self.get_sun_hour(start_date)
        dl = self.get_day_light_length(start_date)
        # cc = self.get_cloud_cover(start_date, start_time, end_time)

        # get sunrise and sunset time
        self.weather_link = "http://118.138.246.158/api/v1/weather"
        # self.location_id = self.location_data[0]['id']

        year = str(start_date)[6:10]
        month = str(start_date)[3:5]
        day = str(start_date)[0:2]
        date_1 = year + "-" + month + "-" + day
        self.weather_PARAMS = {'location': self.location_id, 'date': date_1}
        self.weather_r = requests.get(url=self.weather_link, params=self.weather_PARAMS)
        self.weather_data = self.weather_r.json()
        print(self.weather_data)

        sr = self.weather_data['sunrise']
        ss = self.weather_data['sunset']

        # parse to appropriate format
        sr = int(str(sr[0:2]) + str(sr[3:5]))
        ss = int(str(ss[0:2]) + str(ss[3:5]))

        start_time_hour = int(str(start_time)[0:2])
        start_time_minute = int(str(start_time)[3:5])
        start_time = int(str(start_time[0:2]) + str(start_time[3:5]))

        end_time_hour = int(str(end_time)[0:2])
        end_time_minute = int(str(end_time)[3:5])
        end_time = int(str(end_time[0:2]) + str(end_time[3:5]))

        arr = []

        while start_time_hour <= end_time_hour:
            if start_time_hour == end_time_hour:
                start_time_temp = start_time
                end_time_temp_hour = start_time_hour
                end_time_temp = end_time
                end_time_temp_formatted = str(end_time_temp_hour) + ":" + str(end_time_minute)
            else:
                end_time_temp_hour = start_time_hour + 1
                start_time_temp = start_time
                end_time_temp = int(str(end_time_temp_hour) + "00")
                end_time_temp_formatted = str(end_time_temp_hour) + ":00"

            # print('st', str(start_time_hour)+":"+ str(start_time_minute))
            # print('et', end_time_temp_formatted)
            cc = self.get_cloud_cover(start_date, str(start_time_hour)+":"+ str(start_time_minute),
                                      end_time_temp_formatted)
            if ss >= start_time_temp >= sr:
                if end_time_temp >= ss:
                    du = self.get_duration(str(start_time_temp), str(ss))

                else:
                    du = self.get_duration(str(start_time_temp), str(end_time_temp))

            elif start_time_temp < sr:
                if ss >= end_time_temp >= sr:
                    du = self.get_duration(str(sr), str(end_time_temp))
                elif end_time_temp > ss:
                    du = self.get_duration(str(sr), str(ss))
                else:
                    du = 0
            else:  # = elif start_time > ss
                du = 0

            # print('si', si)
            solar_energy = si * du / dl * (1 - cc / 100) * 50 * 0.20

            arr.append([start_time_temp, end_time_temp, solar_energy])
            start_time_hour += 1
            start_time_minute = 0
            start_time = int(str(start_time_hour) + "00")

        return arr

    def calculate_solar_energy_new_w_cc(self, start_date, start_time, initial_state, final_state,
                                        capacity, power):
        # check the maximum date allowed as input by the calculator, which is two days before the current date
        max_date_allowed = datetime.now() - timedelta(days=2)

        current_date = datetime.strptime(start_date, '%d/%m/%Y')

        date_arr = []
        # put all required dates in date_arr
        if current_date <= max_date_allowed:
            # past
            date_arr.append(current_date)
        else:
            ref_date_per_year = current_date
            # future, so find reference dates
            while ref_date_per_year.year != datetime.now().year:
                ref_date_per_year -= relativedelta(years=1)

            if ref_date_per_year <= current_date:
                # for cases when the nearest reference date (same year) is earlier than today's date
                # eg start_date = 31/8/2022, today's date = 25/9/2021, nearest reference date = 31/8/2021 (valid)
                # thus the reference dates are 31/8/2021, 31/8/2020, 31/8/2019
                for i in range(3):
                    date_arr.append(ref_date_per_year - relativedelta(years=i))
            else:
                # for cases otherwise
                # eg start_date = 25/12/2022, today's date = 25/9/2021, nearest reference date = 25/12/2021 (invalid)
                # thus the reference dates are 25/12/2020, 25/12/2019, 25/12/2018
                for i in range(3):
                    date_arr.append(ref_date_per_year - relativedelta(years=i+1))


        charge_time = self.time_calculation(initial_state, final_state, capacity, power)
        start_time_hour = int(start_time[0:2])
        start_time_minute = int(start_time[3:5])

        charge_time_hour = charge_time * 60 // 60
        charge_time_minute = charge_time * 60 % 60

        end_time_hour = start_time_hour + charge_time_hour
        end_time_minute = start_time_minute + charge_time_minute

        start_time_obj = datetime.strptime(start_time, '%H:%M')
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

        total_res = []
        for date in date_arr:
            arr = str(date.date()).split('-')
            year = arr[0]
            month = arr[1]
            day = arr[2]
            new_start_date = day + "/" + month + "/" + year
            # print(new_start_date)
            res = []
            # within a single day
            if end_time_hour + end_time_minute / 60 <= 23.59:
                # print('end time ', end_time)
                res += (self.calculate_solar_energy_within_a_day_by_hour_w_cc(new_start_date, start_time, end_time))
            else:
                date_time_obj = datetime.strptime(new_start_date + " " + start_time, '%d/%m/%Y %H:%M')
                date_time_after_charge = date_time_obj + timedelta(hours=charge_time)
                start_time_new = start_time

                while date_time_obj.day != date_time_after_charge.day:
                    charge_date_new = str(date_time_obj.date())[8:10] \
                                      + "/" + str(date_time_obj.date())[5:7] \
                                      + "/" + str(date_time_obj.date())[0:4]
                    # temp_duration = timedelta(hours=24) - timedelta(hours=start_time_hour, minutes=start_time_minute)

                    res += (self.calculate_solar_energy_within_a_day_by_hour_w_cc(charge_date_new, start_time_new, "23:59"))
                    date_time_obj += timedelta(days=1)
                    start_time_new = "00:00"

                charge_date_new = str(date_time_obj.date())[8:10] \
                                  + "/" + str(date_time_obj.date())[5:7] \
                                  + "/" + str(date_time_obj.date())[0:4]
                res += (self.calculate_solar_energy_within_a_day_by_hour_w_cc(charge_date_new, start_time_new, end_time))

            # each inner list in total_res contains lists of the time and solar energy generated of that year
            total_res.append(res)

        return total_res

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


# calc = Calculator(5000, "14/09/2021")
# print(calc)
# self.assertEqual(calc.cost_calculation_v2(0,100,20,50,350,"14/09/2021","05:30"),5.5)

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