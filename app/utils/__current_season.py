from datetime import date
from app.ptypes import Station
import datetime

def current_season() -> Station: # type: ignore
    
    stations: dict[Station, list[int]] = {
        "Winter": [12, 1, 2],
        "Spring": [3, 4, 5],
        "Summer": [6, 7, 8],
        "Fall": [9, 10, 11]
    }
    
    for station in stations:
        
        if datetime.datetime.now().month in stations[station]:
            return station