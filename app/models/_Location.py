from . import Point
from dataclasses import dataclass
from pydantic import Field
from typing import Optional

@dataclass
class Location(Point):
    
    location_name: Optional[str] = Field(None, min_length=1, max_length=255, description='Location name')