import re

__all__ = ["ddtodms", "dmstodd"]

def ddtodms(decLat: float, decLon: float):
    """ Converts coord point from decimal degrees to Hddd.mm.ss.sss """
    try:
        lat = float(decLat)
        lon = float(decLon)
    except ValueError as e:
        raise e
    # Get declination
    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"
    lat = abs(lat)
    lon = abs(lon)
    # Floor to get degrees
    latD = int(lat)
    lonD = int(lon)
    # Get minutes
    latM = 60*(lat - latD)
    lonM = 60*(lon - lonD)
    # Get seconds
    latS = 60*(latM - int(latM))
    lonS = 60*(lonM - int(lonM))
    # Assemble output
    latOut = f"{ns}{int(latD):03}.{int(latM):02}.{latS:06.3f}"
    lonOut = f"{ew}{int(lonD):03}.{int(lonM):02}.{lonS:06.3f}"
    return latOut, lonOut

def dmstodd(lat:str, lon:str):
    """ Converts coord point from Hddd.mm.ss.sss to decimal degrees """
    # Check if args are correct type
    if not isinstance(lat, str):
        raise TypeError(repr(lat) + " is not a valid coordinate point. It must be a string")
    if not isinstance(lon, str):
        raise TypeError(repr(lon) + " is not a valid coordinate point. It must be a string")
    # Regex matches
    latPattern = r"([NS])(\d{3})\.(\d{2})\.(\d{2}\.\d{1,3})"
    lonPattern = r"([EW])(\d{3})\.(\d{2})\.(\d{2}\.\d{1,3})"
    latMatch = re.fullmatch(latPattern, lat.strip())
    lonMatch = re.fullmatch(lonPattern, lon.strip())
    # Check if point found
    if not latMatch:
        raise ValueError(repr(lat) + "not a valid lat coordinate")
    if not lonMatch:
        raise ValueError(repr(lon) + "not a valid lon coordinate")
    # Format lat
    ns = "-" if latMatch.group(1)=="S" else ""
    latD = int(latMatch.group(2))
    latM = int(latMatch.group(3))
    latS = float(latMatch.group(4))
    # Format lon
    ew = "-" if lonMatch.group(1)=="W" else ""
    lonD = int(lonMatch.group(2))
    lonM = int(lonMatch.group(3))
    lonS = float(lonMatch.group(4))
    # Convert to decimal degrees
    latOut = ns + str(latD + latM/60 + latS/3600)
    lonOut = ew + str(lonD + lonM/60 + lonS/3600)
    return latOut, lonOut