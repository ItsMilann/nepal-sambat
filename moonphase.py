from skyfield.api import load
from skyfield.framelib import ecliptic_frame

def _get_tithi():
    ts = load.timescale()
    t = ts.utc(2024, 2, 2, 9, 15, 36)

    eph = load("de421.bsp")
    sun, moon, earth = eph["sun"], eph["moon"], eph["earth"]

    e = earth.at(t)
    s = e.observe(sun).apparent()
    m = e.observe(moon).apparent()

    _, slon, _ = s.frame_latlon(ecliptic_frame)
    _, mlon, _ = m.frame_latlon(ecliptic_frame)
    phase = (mlon.degrees - slon.degrees) % 360.0
    return  phase / 12
