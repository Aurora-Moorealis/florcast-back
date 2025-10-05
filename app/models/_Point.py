from typing import Optional
from pydantic import Field
from dataclasses import dataclass

@dataclass
class Point:
    
    # Geographic data
    latitude: float = Field(..., ge=-90, le=90, description="Point Latitude")
    longitude: float = Field(..., ge=-90, le=90, description="Point longitude")