from typing import Optional
from pydantic import Field, BaseModel
from dataclasses import dataclass


class Point(BaseModel):
    
    # Geographic data
    latitude: float = Field(..., ge=-90, le=90, description="Point Latitude")
    longitude: float = Field(..., ge=-90, le=90, description="Point longitude")