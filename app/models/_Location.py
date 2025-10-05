from . import Point
from dataclasses import dataclass
from pydantic import Field
from typing import Optional

@dataclass
class Location(Point):
    
    country_code: Optional[str] = Field(None, min_length=2, max_length=3, description='ISO 3166-1 alpha-2 country code')
    location_name: Optional[str] = Field(None, min_length=1, max_length=255, description='Location name')