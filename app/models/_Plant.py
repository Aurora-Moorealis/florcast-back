from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass
from . import Location
from app.ptypes import Station

class Plant(BaseModel):
    id: int
    scientific_name: str
    common_name: str
    description: str
    max_height: float
    initial_height: float
    temperature_to_grow: float
    growth_rate: float
    bloom_season: str
    created_at: datetime
    updated_at: datetime
    planting_date: datetime
    location: Location
