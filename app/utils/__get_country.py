from geopy.geocoders import Nominatim

def get_country(lat, lon):
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.reverse((lat, lon), language="en") # type: ignore
    
    if location and "country" in location.raw["address"]: # type: ignore
        return location.raw["address"]["country_code"] # type: ignore
    
    return None