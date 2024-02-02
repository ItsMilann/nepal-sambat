# fmt:off
import math
import datetime
import time
import sys

import pytz

tz = pytz.timezone("Asia/Kathmandu")

def j2ts(j: float | int) -> float:
    return (j - 2440587.5) * 86400


def ts2j(ts: float | int) -> float:
    return ts / 86400.0 + 2440587.5


LATITUDE = 27.7172
LONGITUDE = 85.3240
LOCATION = (LONGITUDE, LATITUDE)

AD_EPOCH = 2451545
# tzinfo = pytz.timezone("Asia/Kathmandu")
JULIAN_DATE = ts2j(time.time())
_JD = JULIAN_DATE
print("JULIAN DATE: ", _JD)
DAYS_SINCE_EPOCH = round(JULIAN_DATE - (2451545.0 + 0.0009) + 69.184 / 86400.0)
print("DATE SINCE EPOCH: ", DAYS_SINCE_EPOCH)
MEAN_SOLAR_TIME = DAYS_SINCE_EPOCH + 0.0009 - LONGITUDE / 360
print("MEAN SOLAR TIME: ", MEAN_SOLAR_TIME)
SOLAR_MEAN_ANAMOLY = math.fmod(357.5291 + 0.98560028 * MEAN_SOLAR_TIME, 360)
_M = SOLAR_MEAN_ANAMOLY
print("SOLAR MEAN ANAMOLY", _M)
CENTER = (
    1.9148 * math.sin(math.radians(_M))
    + 0.0200 * math.sin(math.radians(2 * _M))
    + 0.0003 * math.sin(math.radians(3 * _M))
)
_C = CENTER

ECLIPTIC_LONG = math.fmod(_M + _C + 180 + 102.9372, 360)
_LAMBDAe = ECLIPTIC_LONG
print("ECLIPTIC_LONG", ECLIPTIC_LONG)
SOLAR_TRANSIT = (
    AD_EPOCH
    + MEAN_SOLAR_TIME
    + 0.0053 * math.sin(math.radians(SOLAR_MEAN_ANAMOLY))
    - 0.0069 * math.sin(2 * math.radians(_LAMBDAe))
)
print("SOLAR TRANSIT", SOLAR_TRANSIT)


DECLINATION_OF_SUN = math.sin(math.radians(_LAMBDAe)) * math.sin(math.radians(23.4397))
_DELTA = math.degrees(math.asin(DECLINATION_OF_SUN))
COS_D = math.cos(math.asin(DECLINATION_OF_SUN))
_A = math.sin(math.radians(-0.833))- math.sin(math.radians(LATITUDE)) * DECLINATION_OF_SUN
_B = math.cos(math.radians(LATITUDE)) * COS_D
HOUR_ANGLE = math.acos(_A/_B)
_OMEGAo = HOUR_ANGLE
print("HOUR ANGLE", math.degrees(_OMEGAo))
SUNSET = SOLAR_TRANSIT + math.degrees(_OMEGAo) / 360
SUNRISE = SOLAR_TRANSIT - math.degrees(_OMEGAo) / 360
print("SUNRISE: ", datetime.datetime.fromtimestamp(j2ts(SUNRISE)))
print("SUNSET: ", datetime.datetime.fromtimestamp(j2ts(SUNSET)))


#############
TITHI_LIST = ["आमै", "पार", "िदतीया", "तृतीया", "चतुथी", "पञमी", "षषी", "सपमी", "अषमी", "नवमी",
              "दशमी", "एकादशी", "दादशी", "तयोदशी", "चतुदरशी", "पुिन"]

NS_MONTHS = ["कछला","िथंला","पँहेला","िसला","िचला","चौला","बछला","तछला","िदला","गुंला","ञला","कौला"]

import ephem

tau = 2.0 * ephem.pi
gatech = ephem.Observer()
gatech.lon = LONGITUDE
gatech.lat = LATITUDE
gatech.elevation = 0

for i in range(0, 30):
    _date = datetime.datetime.fromtimestamp(j2ts(SUNRISE))
    _date = _date + datetime.timedelta(days=i)
    gatech.date = _date # datetime.datetime.fromtimestamp(j2ts(SUNRISE))
    # datetime.datetime.today() - datetime.timedelta(days=3)
    print(_date.strftime("%Y/%m/%d"), end="\t")
    moon_x = ephem.Moon(gatech)
    sun_x = ephem.Sun(gatech)
    sunlon_x = ephem.Ecliptic(sun_x).lon
    moonlon_x = ephem.Ecliptic(moon_x).lon
    LUNAR_ANGLE_X = math.degrees(moonlon_x - sunlon_x)

    PREVIOUS_NEW_MOON_DATE = ephem.previous_new_moon(_date)
    gatech.date = PREVIOUS_NEW_MOON_DATE
    sun = ephem.Sun(gatech)
    sunlon_at_new_moon = ephem.Ecliptic(sun).lon
    month = round(math.degrees(sunlon_at_new_moon) / 30)
    corrected_month = math.ceil(month) - 8

    _yesterday = _date - datetime.timedelta(days=i)
    gatech.date = _yesterday
    moon_y = ephem.Moon(gatech)
    sun_y = ephem.Sun(gatech)
    sunlon_y = ephem.Ecliptic(sun_y).lon
    moonlon_y = ephem.Ecliptic(moon_y).lon
    LUNAR_ANGLE_Y = math.degrees(moonlon_y - sunlon_y)

    tithi_today = LUNAR_ANGLE_X / 12
    tithi_yesterday = LUNAR_ANGLE_Y / 12
    tithi = round(tithi_today)

    PAKSHYA = "tho" if tithi <= 15 else "ga"
    PAKSHYA_DEV = " (थ)" if PAKSHYA == "tho" else " (गा)"
    print(NS_MONTHS[corrected_month] + PAKSHYA_DEV,  end=", ")
    if tithi < 0:
        tithi = 15 + tithi
    if PAKSHYA == "ga":
        tithi = tithi - 15

    tithi = abs(tithi)
    print(TITHI_LIST[round(tithi)], end="\t")

    if round(tithi_today) == round(tithi_yesterday):
        print("\tT: ", 8, end="\t")
    elif round(tithi_today) - round(tithi_yesterday) == 2:
        print("\tT: ", 9, end="\t")
    else:
        print("\tT: ", 0, end="\t")

    DAYS_SINCE_KALIYUG = _JD - 588465.5
    KALI_YEAR = math.floor((DAYS_SINCE_KALIYUG + (10 - math.floor(month)) * 30) / 365.25636)
    SAKA_YEAR = KALI_YEAR - 3179
    NS_YEAR = SAKA_YEAR - 801 # 2 is corrected value

    print(NS_YEAR, "YEAR")
