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

    def cost_calculation_v1(self, initial_state, final_state, capacity,base_price,power,start_date,start_time):
        # requirement 2 can't take in future dates, so just return a '-'
        max_date_allowed = datetime.now() - timedelta(days=2)

        current_date = datetime.strptime(start_date, '%d/%m/%Y')

        if current_date <= max_date_allowed:
            pass
        else:
            return '-'
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
            total_power = max((((float(final_state) - float(initial_state)) / 100) * float(capacity)),0)
            total_cost = total_power * price / 100 * surcharge
            return total_cost
        else :
            price = base_price*0.5 if not self.is_peak_v2(current_datetime) else base_price
            surcharge = surcharge_factor if self.is_holiday_v2(current_datetime) else 1
            partial_initial_state = float(initial_state)
            partial_final_state = partial_initial_state + ((float(final_state) - float(initial_state))/total_time) * hour_difference
            total_power = max(((partial_final_state-partial_initial_state)/100) * float(capacity),0)
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
                total_power = max(((partial_final_state-partial_initial_state)/100) * float(capacity),0)
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
                total_power = max(((partial_final_state-partial_initial_state)/100)* float(capacity) ,0)
                total_cost += total_power* price / 100 * surcharge
            return round(total_cost,2)

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
                total_cost += total_power * price / 100 * surcharge
                # return total_cost
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

        return round(total_cost/len(power_list), 2)

    # you may add more parameters if needed, you may also modify the formula.
    def time_calculation(self, initial_state, final_state, capacity, power):
        """
        Function that calculates the duration to charge the vehicle from initial_state to final_state given its battery capacity
        and power supplied by the charger
        :param initial_state : float between 0 and 100 at most equal to final_state 
        :param final_state   : float between 0 and 100 at least equal to initial_state
        :param capacity      : float between 0.65 and 100
        :param power         : float value according to available charger configurations
        :return              : float representation of charging time required correct to two decimal places in hours
        """
        time = (float(final_state) - float(initial_state)) / 100 * float(capacity) / power
        return round(time, 2)

    # you may create some new methods at your convenience, or modify these methods, or choose not to use them.
    def is_holiday_v2(self, start_date):
        """
        Function that determines if a given date is deemed to be a surchargable date in Australia or not
        :param start_date   : datetime object representing the starting date for charging
        :return             : True if start_date is an Australian holiday or weekday, False otherwise
        """
        aus_holidays = holidays.Australia()     # generate a set of dates which represent holidays in Australia
        return start_date in aus_holidays or start_date.weekday() <= 4

    def is_peak_v2(self, start_time):
        """
        Function that determines if given time falls within designated peak hours or not
        :param start_time   : datetime object representing the starting time for charging
        :return             : True if start_time falls within peak time hours, False otherwise
        """
        non_peak_time_1 = datetime(start_time.year, start_time.month, start_time.day, 6, 0, 0)  # 6:00 A.M. / 0600 hrs
        non_peak_time_2 = datetime(start_time.year, start_time.month, start_time.day, 18, 0, 0) # 6:00 P.M. / 1800 hrs
        return non_peak_time_1 <= start_time <= non_peak_time_2

    # to be acquired through API
    def get_sun_hour(self, start_date):
        """
        Function that retrieves the solar insulation value from the online API given the provided datetime and charging
        location
        :param start_date   : string representing the starting date for charging in DD/MM/YYYY format
        :return             : the solar insolation or sun hour value for the given starting charging date and location
        """
        # API endpoint for weather data
        self.weather_link = "http://118.138.246.158/api/v1/weather"

        # extracting each component from the date for reformatting
        year = str(start_date)[6:10]
        month = str(start_date)[3:5]
        day = str(start_date)[0:2]
        date_1 = year + "-" + month + "-" + day

        # setting the parameter values for location and date before calling a GET request from the API to obtain the
        # weather data for that particular date in that location
        self.weather_PARAMS = {'location': self.location_id, 'date': date_1}
        self.weather_r = requests.get(url=self.weather_link, params=self.weather_PARAMS)
        self.weather_data = self.weather_r.json()
        self.sun_hour = self.weather_data['sunHours']

        return self.sun_hour

    # to be acquired through API
    def get_day_light_length(self, start_date):
        """
        Function that provides the duration of daylight for the given date (time between sunrise and sunset) in hours by
        obtaining the sunrise and sunset times for the given date through the API
        :param start_date   : string representing the starting date for charging in DD/MM/YYYY format
        :return             : the duration of daylight for the given date in hours
        """
        # API endpoint for weather data
        self.weather_link = "http://118.138.246.158/api/v1/weather"

        # extracting each component from the date for reformatting
        date = start_date.split('/')
        year = date[2]
        month = date[1]
        day = date[0]
        date_1 = year + "-" + month + "-" + day

        # setting the parameter values for location and date before calling a GET request from the API to obtain the
        # weather data for that particular date in that location
        self.weather_PARAMS = {'location': self.location_id, 'date': date_1}
        self.weather_r = requests.get(url=self.weather_link, params=self.weather_PARAMS)
        self.weather_data = self.weather_r.json()

        # format the extracted data such that it is in the form [hour, minute, seconds]
        sunrise_time = self.weather_data['sunrise'].split(':')  # sunrise_time_format : 05:10:00
        sunset_time = self.weather_data['sunset'].split(':')    # sunset_time_format : 19:24:00

        # extracting the hour and minute components of the sunrise and sunset times
        sunrise_hour = int(sunrise_time[0])
        sunrise_minute = int(sunrise_time[1])

        sunset_hour = int(sunset_time[0])
        sunset_minute = int(sunset_time[1])

        # time readjustment so that sunset_minute is always >= sunrise_minute for subtraction purposes
        if sunset_minute < sunrise_minute:
            sunset_minute += 60
            sunset_hour -= 1

        return (sunset_hour - sunrise_hour) + (sunset_minute - sunrise_minute)/60

    def get_cloud_cover(self, start_date, start_time, end_time):
        """
        Function that retrieves the cloud cover value from the API based on the given starting charging date and time given
        that the start_time and end_time fall within the same hour
        :param start_date   : string representing the starting date for charging in DD/MM/YYYY format
        :param start_time   : string representing the starting time for charging in HH24:MM format
        :param end_time     : string representing the ending time for charging in HH24:MM format
        :return             : the cloud cover value on start_date during the hour represented in start_time
        """
        # API endpoint for weather data
        self.weather_link = "http://118.138.246.158/api/v1/weather"

        # converting start_date into a datetime object and ensuring the month component is represented by two digits
        date_time_obj = datetime.strptime(start_date, '%d/%m/%Y')
        month = str(date_time_obj.month)
        if len(month) != 2:
            month = "0" + month
        else:
            pass
        
        # ensuring the day component is represented by two digits
        day = str(date_time_obj.day)
        if len(day) != 2:
            day = "0" + day
        else:
            pass
        
        # setting the parameter values for location and date before calling a GET request from the API to obtain the
        # weather data for that particular date in that location
        new_date = str(date_time_obj.year) + "-" + month + "-" + day
        self.weather_PARAMS = {'location': self.location_id, 'date': new_date}
        self.weather_r = requests.get(url=self.weather_link, params=self.weather_PARAMS)
        self.weather_data = self.weather_r.json()

        # per hour basis
        start_time = start_time.split(':')  # start time format 03:22 -> [3,22]
        start_time_hour = int(start_time[0])
        start_time_as_integer = int(start_time[0] + start_time[1])

        end_time = end_time.split(':')  # end time format 03:22 -> [3,22]
        end_time_as_integer = int(end_time[0] + end_time[1])

        # check to ensure end_time is at least equal to start_time
        if end_time_as_integer < start_time_as_integer:
            raise ValueError("End time cannot be earlier than start time")
        else:
            cc = 0
            # iterate through the cloud cover data for each hour in the json object and assign the cloud cover value
            # for the hour that matches that of the given start_time, else maintain the cloud cover at 0
            for i in range(24):
                if self.weather_data["hourlyWeatherHistory"][i]["hour"] == start_time_hour:
                    cc = self.weather_data["hourlyWeatherHistory"][i]["cloudCoverPct"]
                    return cc
                else:
                    pass

            return cc

    def get_duration(self, start_time, end_time):
        """
        Function that calculates the duration between the given start_time and end_time in hours
        :param start_time   : string representing the starting time for charging, eg: "730", "1640", "20"
        :param end_time     : string representing the ending time for charging
        :return             : the duration between start_time and end_time in hours
        """
        # extracting the hour and minute components (if any) from the given starting time string
        start_time_hour = 0
        if len(start_time) == 1 or len(start_time) == 2:    # no hour component
            start_time_minute = start_time
        elif len(start_time) == 3:  # hour component in single digit
            start_time_minute = start_time[-2:]
            start_time_hour = start_time[0]
        else:   # hour component in double digits
            start_time_minute = start_time[-2:]
            start_time_hour = start_time[0:2]

        # extracting the hour and minute components (if any) from the given ending time string
        end_time_hour = start_time_hour
        if len(end_time) == 1 or len(end_time) == 2:
            end_time_minute = start_time
        elif len(end_time) == 3:    # hour component in single digit
            end_time_minute = end_time[-2:]
            end_time_hour = end_time[0]
        else:   # hour component in double digits
            end_time_minute = end_time[-2:]
            end_time_hour = end_time[0:2]

        # convert each hour and minute components into integers
        start_time_hour = int(start_time_hour)
        start_time_minute = int(start_time_minute)
        end_time_hour = int(end_time_hour)
        end_time_minute = int(end_time_minute)

        # time readjustment so that end_time_minute is always >= start_time_minute for subtraction purposes
        if end_time_minute < start_time_minute:
            end_time_minute += 60
            end_time_hour -= 1

        du_minute = end_time_minute - start_time_minute
        du_hour = end_time_hour - start_time_hour

        # ensuring the minute component of the duration is always double digits
        if len(str(du_minute)) == 1:
           du_minute = '0' + str(du_minute)
        else:
            pass

        du = int(str(du_hour) + str(du_minute))

        if len(str(du)) == 1 or len(str(du)) == 2:  # convert to hours
            final_du = du / 60  
        elif len(str(du)) == 3: # convert minute component to hours
            final_du = int(str(du)[0]) + int(str(du)[1:3]) / 60
        else:   # convert minute component to hours
            final_du = int(str(du)[0:2]) + int(str(du)[2:4]) / 60

        return final_du

    # --------------------------------- Requirement 2 -----------------------------------
    def calculate_solar_energy_within_a_day_by_hour(self, start_date, start_time, end_time):
        """
        Function that calculates the solar energy received on an hourly basis based on the given starting date and charging
        start and end times
        :param start_date   : string representing the starting date for charging in DD/MM/YYYY format
        :param start_time   : string representing the starting time for charging in HH24:MM format
        :param end_time     : string representing the ending time for charging in HH24:MM format
        :return             : an array containing arrays that represent the solar energy generated for each hour from start_time
                              to end_time
        """
        # get solar hour/insolation (si) and daylight length (dl)
        si = self.get_sun_hour(start_date)
        dl = self.get_day_light_length(start_date)

        # API endpoint for weather data
        self.weather_link = "http://118.138.246.158/api/v1/weather"

        # extracting each component from the date for reformatting
        year = str(start_date)[6:10]
        month = str(start_date)[3:5]
        day = str(start_date)[0:2]
        date_1 = year + "-" + month + "-" + day

        # setting the parameter values for location and date before calling a GET request from the API to obtain the
        # weather data for that particular date in that location
        self.weather_PARAMS = {'location': self.location_id, 'date': date_1}
        self.weather_r = requests.get(url=self.weather_link, params=self.weather_PARAMS)
        self.weather_data = self.weather_r.json()

        # sunrise and sunset time from the retrieved weather data json object
        sr = self.weather_data['sunrise']
        ss = self.weather_data['sunset']

        # conversion of sunrise and sunset time to integer in required format
        sr = int(str(sr[0:2]) + str(sr[3:5]))
        ss = int(str(ss[0:2]) + str(ss[3:5]))

        # extracting the hour component of start_time and compressing it into a single integer
        start_time_hour = int(str(start_time)[0:2])
        start_time = int(str(start_time[0:2]) + str(start_time[3:5]))

        # extracting the hour component of end_time and compressing it into a single integer
        end_time_hour = int(str(end_time)[0:2])
        end_time = int(str(end_time[0:2]) + str(end_time[3:5]))

        arr = []
        while start_time_hour <= end_time_hour: # calculate solar energy generated on hourly basis
            if start_time_hour == end_time_hour:    # start_time and end_time within the same hour
                start_time_temp = start_time
                end_time_temp = end_time
            else:   # start_time and end_time different hours
                end_time_temp_hour = start_time_hour + 1
                start_time_temp = start_time
                end_time_temp = int(str(end_time_temp_hour) + "00")

            if ss >= start_time_temp >= sr: # starting time in between sunrise and sunset
                if end_time_temp >= ss: # solar energy non-existent for time beyond sunset
                    du = self.get_duration(str(start_time_temp), str(ss))
                else:
                    du = self.get_duration(str(start_time_temp), str(end_time_temp))
            elif start_time_temp < sr:
                if ss >= end_time_temp >= sr:
                    du = self.get_duration(str(sr), str(end_time_temp))
                elif end_time_temp > ss:
                    du = self.get_duration(str(sr), str(ss))
                else:   # period exists before sunrise
                    du = 0
            else: # start_time > ss
                du = 0

            solar_energy = si * du / dl * 50 * 0.2

            arr.append([start_time_temp, end_time_temp, solar_energy])
            start_time_hour += 1
            start_time = int(str(start_time_hour) + "00")

        return arr

    def calculate_solar_energy_new(self, start_date, start_time, initial_state, final_state, capacity, power):
        """
        Function that calculates the solar energy generated during the charging period required to bring the battery level from
        the initial state to the final state given its capacity and power provided by the charger
        :param start_date   : string representing the starting date for charging in DD/MM/YYYY format
        :param start_time   : string representing the starting time for charging in HH24:MM format
        :param initial_state: float between 0 and 100 at most equal to final_state 
        :param final_state  : float between 0 and 100 at least equal to initial_state
        :param capacity     : float between 0.65 and 100
        :param power        : float value according to available charger configurations
        :return             : an array of arrays each representing the hourly solar energy values for each day elapsed during the
                              charging duration
        """
        # obtaining the charging time required to provided enough energy to go from initial to final state
        charge_time = self.time_calculation(initial_state, final_state, capacity, power)

        # extracting the hour and minute components of the start_time
        start_time_hour = int(start_time[0:2])
        start_time_minute = int(start_time[3:5])

        # extracting the hour and minute components of the charging time
        charge_time_hour = charge_time * 60 // 60
        charge_time_minute = charge_time * 60 % 60

        # calculating the hour and minute components of the ending time after charging
        end_time_hour = start_time_hour + charge_time_hour
        end_time_minute = start_time_minute + charge_time_minute

        # conversion of the starting and ending times into datetime objects
        start_time_obj = datetime.strptime(start_time, '%H:%M')
        end_time_obj = start_time_obj + timedelta(hours=charge_time_hour, minutes=charge_time_minute)

        end_time = str(end_time_obj.time())[0:5]

        res = []
        if end_time_hour + end_time_minute / 60 <= 23.59:   # within a single day
            res += (self.calculate_solar_energy_within_a_day_by_hour(start_date, start_time, end_time))
        else:   # charging spanning more than a day
            date_time_obj = datetime.strptime(start_date + " " + start_time, '%d/%m/%Y %H:%M')
            date_time_after_charge = date_time_obj + timedelta(hours=charge_time)
            start_time_new = start_time

            # obtaining the hourly solar energy values for each day elapsed between the start_time and end_time
            while date_time_obj.day != date_time_after_charge.day:
                charge_date_new = str(date_time_obj.date())[8:10] \
                                  + "/" + str(date_time_obj.date())[5:7] \
                                  + "/" + str(date_time_obj.date())[0:4]

                res += (self.calculate_solar_energy_within_a_day_by_hour(charge_date_new, start_time_new, "23:59"))
                date_time_obj += timedelta(days=1)  # proceed to the next day
                start_time_new = "00:00"

            # hourly solar energy values for the final day
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
            solar_energy = round(si * du / dl * (1 - cc / 100) * 50 * 0.20, 11)
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
    def get_power(self, charger_configuration):
        """
        Function that outputs the correct power value for the given charger configuration
        :param charger_configuration    : integer representation of a charger configuration
        :return                         : power output for the given charger configuration
        """
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
        else:
            return 350

    def get_price(self, charger_configuration):
        """
        Function that outputs the correct price value for the given charger configuration
        :param charger_configuration    : integer representation of a charger configuration
        :return                         : price for the given charger configuration
        """
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
        else:
            return 50
