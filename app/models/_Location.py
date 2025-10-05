from . import Point
from dataclasses import dataclass
from pydantic import Field, BaseModel
from typing import Optional


class Location(BaseModel):
    
    country_code: Optional[str] = Field(None, min_length=2, max_length=3, description='ISO 3166-1 alpha-2 country code')
    location_name: Optional[str] = Field(None, min_length=1, max_length=255, description='Location name')
    coords: Point