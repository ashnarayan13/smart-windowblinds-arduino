#import numpy as np
import time
from datetime import datetime


# TRUE is OPEN
# FALSE is CLOSE


maximum_outside_summer_temperature = 23
minimum_outside_winter_temperature = 12
minimum_inside_winter_temperature = 23
maximum_inside_summer_temperature = 23
maximum_uv_index = 4
sun_azimuth_angle_1 = 40
sun_azimuth_angle_2 = 140
sun_altitude = 30
clear_sky = 0
scatter_clouds = 0.4
broken_clouds = 0.75
overcast_sky = 1
clear_sky_position = 0 #fully closed
overcast_position = 100 #fully open

# user overide parameters

# daily
user_override_daily_min_temperature_threshold = 0
user_override_daily_min_position_threshold = 0
user_override_daily_max_temperature_threshold = 30
user_override_daily_max_position_threshold = 100

# season based

user_override_winter_min_temperature_threshold = 10
user_override_summer_max_temperature_threshold = 25

# energy save time threshold
opening_time = "7:00"
closing_time = "19:00"


def check_azimuth(azim):
    if azim > sun_azimuth_angle_1 and azim < sun_azimuth_angle_2:
        return False
    else:
        return True


def check_altitude(altitude):
    if altitude > sun_altitude:
        return False
    else:
        return True


def check_temp_summer(in_t, out_t):
    if in_t > maximum_inside_summer_temperature and out_t > maximum_outside_summer_temperature:
        return False
    else:
        return True


def check_temp_winter(in_t, out_t):
    if in_t < minimum_inside_winter_temperature and out_t < minimum_outside_winter_temperature:
        return False
    else:
        return True


def check_cloud(cloud):
    pass


def check_uv(uv):
    if uv>maximum_uv_index:
        return False
    else:
        return True


# TRUE - open
# FALSE - close

def justBasic(inside_ir, inside_vis):
    if inside_ir < 300:
        return False
    if inside_vis < 270:
        return False
    return True

def calculate_movement(season, outside_temperature, solar_azimuth, solar_altitude, cloud_cover_percentage,
                       inside_temperature, inside_humidity, inside_uv, inside_ir, inside_vis):

    if inside_ir>300:
        return False
    if inside_vis>270:
        return False
    return True
    temperature = False
    azimuth = False
    altitude = False
    uv = False
    flag_winter = False

    if season == "winter":
        flag_winter = True
    else:
        flag_winter = False

    current_time = time.time()
    current_time_new = str(current_time.hour) + ':' + str(current_time.minute)

    if current_time_new < opening_time or current_time_new > closing_time:
        flag_energy_save = True
    else:
        flag_energy_save = False

    if flag_winter:
        temperature = check_temp_winter(inside_temperature, outside_temperature)
    else:
        temperature = check_temp_summer(inside_temperature, outside_temperature)

    azimuth = check_azimuth(solar_azimuth)
    altitude = check_altitude(solar_altitude)
    uv = check_uv(inside_uv)
    # check closing and opening time close blinds
    # action = False
    if azimuth and altitude:
        return False  # potentially move blinds upward

    if temperature:
        return True

    if uv:
        return False

    if flag_energy_save:
        return False

    #return False
    return True
