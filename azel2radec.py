#!/usr/bin/env python3
from __future__ import division
from numpy import sin, cos, degrees, radians,arcsin, arctan2, atleast_1d, nan
import sys

usevallado = False
if usevallado:
    sys.path.append('../astrometry') # git clone https://github.com/scienceopen/astrometry/
    from datetime2hourangle import datetime2sidereal
else: #astropy
    from astropy import units as u
    from astropy.time import Time
    from astropy.coordinates import SkyCoord, EarthLocation, AltAz, ICRS

"""
Michael Hirsch
GPLv3+
"""
    
def azel2radec(az_deg, el_deg, lat_deg, lon_deg, dtime):

    """ from D.Vallado Fundamentals of Astrodynamics and Applications p.258-259 """
    az_deg = atleast_1d(az_deg)
    el_deg = atleast_1d(el_deg)
    lat_deg = atleast_1d(lat_deg)
    lon_deg = atleast_1d(lon_deg)

    if az_deg.shape != el_deg.shape: exit('az and el must be same shape')
    if lat_deg.shape != lon_deg.shape: exit('lat and lon must be same shape')

    if usevallado:
        ra_deg, dec_deg = azel2radecvallado(az_deg,el_deg,lat_deg,lon_deg,dtime)
    else: #use astropy v1.0 + 
        obs = EarthLocation(lat=lat_deg*u.deg, lon=lon_deg*u.deg)
        direc = AltAz(location=obs, obstime=Time(dtime), 
                      az=az_deg*u.deg, alt=el_deg*u.deg)
        sky = SkyCoord(direc.transform_to(ICRS()))
        ra_deg = sky.ra.deg
        dec_deg = sky.dec.deg
            
        
    return ra_deg, dec_deg
        
def azel2radecvallado(az_deg,el_deg,lat_deg,lon_deg,dtimen):
    az = radians(az_deg); el = radians(el_deg)
    lat = radians(lat_deg); lon = radians(lon_deg)
     #Vallado "algorithm 28" p 268
    dec = arcsin( sin(el) * sin(lat) + cos(el) * cos(lat) * cos(az) )

    lha = arctan2( -(sin(az) * cos(el)) / cos(dec),
                   (sin(el) - sin(lat)*sin(dec)) / (cos(dec) * cos(lat)) )

    lst = datetime2sidereal(dtime,lon) #lon, ra in RADIANS

    """ by definition right ascension \in [0,360) degrees """
    return degrees(lst - lha) % 360, degrees(dec)

if __name__ == "__main__":
    from dateutil.parser import parse
    from argparse import ArgumentParser

    p = ArgumentParser(description='convert azimuth and elevation to right ascension and declination')
    p.add_argument('azimuth',help='azimuth [degrees]',nargs='?',type=float,default=nan)
    p.add_argument('elevation',help='elevation [degrees]',nargs='?',type=float,default=nan)
    p.add_argument('lat',help='WGS84 latitude of observer [deg] ',nargs='?',type=float,default=nan)
    p.add_argument('lon',help='WGS84 longitude of observer [deg.]',nargs='?',type=float,default=nan)
    p.add_argument('time',help='time of observation YYYY-mm-ddTHH:MM:SSZ',nargs='?',type=str,default='')
    p.add_argument('--selftest',help='integration test',action='store_true')
    a = p.parse_args()

    if a.selftest:
        from numpy.testing import assert_allclose
        ra,dec = azel2radec(180.1, 80, 65, -148,parse('2014-04-06T08:00:00Z'))
        assert_allclose(ra,166.5032081149338,rtol=1e-2)
        assert_allclose(dec,55.000011165405752,rtol=1e-2)
    else:

        dtime = parse(a.time)
        print(dtime)
    
        ra,dec = azel2radec(a.azimuth,a.elevation,a.lat,a.lon,dtime)
        print('ra / dec =',(ra,dec) )
