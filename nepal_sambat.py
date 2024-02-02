# fmt:off
import math
import datetime
import ephem
import argparse
import pytz
import sys

tz = pytz.timezone("Asia/Kathmandu")

_TDateTime = datetime.datetime

LATITUDE = 27.7172
LONGITUDE = 85.3240
AD_EPOCH = 2451545


gatech = ephem.Observer()
gatech.lon = LONGITUDE
gatech.lat = LATITUDE
gatech.elevation = 0


def j2ts(j: float | int) -> float:
    """convert julian date to timestamp"""
    return (j - 2440587.5) * 86400


def ts2j(ts: float | int) -> float:
    "convert timestamp to julian date"
    return ts / 86400.0 + 2440587.5


def _get_sun_time(dt:_TDateTime) -> tuple[_TDateTime, _TDateTime]:

    JULIAN_DATE = ts2j(dt.timestamp())
    DAYS_SINCE_EPOCH = round(JULIAN_DATE - (2451545.0 + 0.0009) + 69.184 / 86400.0)
    MEAN_SOLAR_TIME = DAYS_SINCE_EPOCH + 0.0009 - LONGITUDE / 360
    SOLAR_MEAN_ANAMOLY = math.fmod(357.5291 + 0.98560028 * MEAN_SOLAR_TIME, 360)
    _M = SOLAR_MEAN_ANAMOLY
    CENTER = (
        1.9148 * math.sin(math.radians(_M))
        + 0.0200 * math.sin(math.radians(2 * _M))
        + 0.0003 * math.sin(math.radians(3 * _M))
    )
    _C = CENTER

    ECLIPTIC_LONG = math.fmod(_M + _C + 180 + 102.9372, 360)
    _LAMBDAe = ECLIPTIC_LONG
    SOLAR_TRANSIT = (
        AD_EPOCH
        + MEAN_SOLAR_TIME
        + 0.0053 * math.sin(math.radians(SOLAR_MEAN_ANAMOLY))
        - 0.0069 * math.sin(2 * math.radians(_LAMBDAe))
    )
    DECLINATION_OF_SUN = math.sin(math.radians(_LAMBDAe)) * math.sin(math.radians(23.4397))
    COS_D = math.cos(math.asin(DECLINATION_OF_SUN))
    _A = math.sin(math.radians(-0.833))- math.sin(math.radians(LATITUDE)) * DECLINATION_OF_SUN
    _B = math.cos(math.radians(LATITUDE)) * COS_D
    HOUR_ANGLE = math.acos(_A/_B)
    _OMEGAo = HOUR_ANGLE
    SUNSET = SOLAR_TRANSIT + math.degrees(_OMEGAo) / 360
    SUNRISE = SOLAR_TRANSIT - math.degrees(_OMEGAo) / 360
    sunrise = datetime.datetime.fromtimestamp(j2ts(SUNRISE))
    sunset = datetime.datetime.fromtimestamp(j2ts(SUNSET))
    return sunrise, sunset


#############
TITHI_LIST = ["पुिन", "पार", "िदतीया", "तृतीया", "चतुथी", "पञमी", "षषी", "सपमी", "अषमी", "नवमी",
              "दशमी", "एकादशी", "दादशी", "तयोदशी", "चतुदरशी", "आमै"]

NS_MONTHS = ["कछला","िथंला","पँहेला","िसला","िचला","चौला","बछला","तछला","िदला","गुंला","ञला","कौला"]

from skyfield.api import load
from skyfield.framelib import ecliptic_frame


def _get_tithi(dt:datetime.datetime):
    ts = load.timescale()
    # t = ts.utc(int(dt.year), int(dt.month), int(dt.day), int(dt.hour), int(dt.minute), int(dt.second))
    t = ts.from_datetime(dt)

    eph = load("de421.bsp")
    sun, moon, earth = eph["sun"], eph["moon"], eph["earth"]

    e = earth.at(t)
    s = e.observe(sun).apparent()
    m = e.observe(moon).apparent()

    _, slon, _ = s.frame_latlon(ecliptic_frame)
    _, mlon, _ = m.frame_latlon(ecliptic_frame)
    phase = (mlon.degrees - slon.degrees) % 360.0
    return  phase / 12


def _get_month(dt: _TDateTime):
    ...

def get_nepal_sambat(dt:_TDateTime):
    SUNRISE, _ = _get_sun_time(dt)
    _JD = ts2j(dt.timestamp())
    _date = SUNRISE
    print(_date.strftime("%Y/%m/%d"), end="\t")
    gatech.date = ephem.previous_new_moon(_date)
    sun = ephem.Sun(gatech)
    sunlon_at_new_moon = ephem.Ecliptic(sun).lon
    month = round(math.degrees(sunlon_at_new_moon) / 30)
    corrected_month = math.ceil(month) - 8
    tithi_today =  _get_tithi(dt)
    print("TITHI", tithi_today, end="\t")
    tithi_today = round(tithi_today)
    tithi_yesterday = _get_tithi((dt - datetime.timedelta(days=1)))
    tithi_yesterday = math.ceil(tithi_yesterday)
    PAKSHYA = 1 if tithi_today <= 15 else 2
    PAKSHYA_DEV = " (थ)" if PAKSHYA == 1 else " (गा)"
    print(NS_MONTHS[corrected_month] + PAKSHYA_DEV,  end=", ")

    if PAKSHYA == 2:
        tithi_today = tithi_today - 15

    if tithi_today in [15, 0]:
        tithi_today = 0 if PAKSHYA == 1 else 15
        
    print(TITHI_LIST[tithi_today] + "\t" + str(tithi_today), end="\t")

    if round(tithi_today) == round(tithi_yesterday):
        print("\tT: ", 8, end="\t")
    elif round(tithi_today) - round(tithi_yesterday) == 2:
        print("\tT: ", 9, end="\t")
    else:
        print("\tT: ", 0, end="\t")

    DAYS_SINCE_KALIYUG = _JD - 588465.5
    KALI_YEAR = math.floor((DAYS_SINCE_KALIYUG + (10 - math.floor(month)) * 30) / 365.25636)
    SAKA_YEAR = KALI_YEAR - 3179
    NS_YEAR = SAKA_YEAR - 799 # 2 is corrected value

    print(NS_YEAR, "YEAR")

err = 'error: required YYYY-MM-DD date format'
parser = argparse.ArgumentParser(description='Optional app description')
parser.add_argument('pos_arg', type=str, help=err)
args = parser.parse_args()
if not args:
    print(err)
_date = args.pos_arg
try:
    dt = datetime.date.fromisoformat(_date)
except ValueError:
    print(err)
    sys.exit()
dt = datetime.datetime.now().replace(year=dt.year, month=dt.month, day=dt.day)
get_nepal_sambat(tz.localize(dt))
