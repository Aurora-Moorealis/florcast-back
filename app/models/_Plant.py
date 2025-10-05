from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass
from . import Location, Point
from app.ptypes import Station

@dataclass
class Plant:
    scientific_name: list[str] = Field([], min_length=1, max_length=200, description="Scientific name of the plant")
    common_name: str = Field(..., min_length=1, max_length=100, description="Common name of the plant")
    family: str = Field(..., min_length=1, max_length=100, description="Plant family")
    description: Optional[str] = Field(None, max_length=1000, description="Plant description")
    
    # Plant characteristics
    max_height: Optional[float] = Field(None, gt=0, description="Average height in centimeters")
    initial_height: Optional[float] = Field(None, gt=0, description="Current height in centimeters")
    
    temperature_to_grow: Optional[float] = Field(None, description="Optimal temperature to grow in Celsius")
    growth_rate: Optional[float] = Field(None, gt=0, description="Growth Rate in centimeters")
    bloom_season: list[Station] = Field([], max_length=100, description="Blooming season")

class PlantBase(Plant, Location, BaseModel):
    """Base plant model"""
    ...


class PlantCreate(Plant, BaseModel):
    """Model for creating a plant"""
    pass


class PlantUpdate(BaseModel):
    """Model for updating a plant"""
    scientific_name: Optional[list[str]] = Field(None, min_length=1, max_length=200)
    common_name: Optional[str] = Field(None, min_length=1, max_length=100)
    family: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    max_height: Optional[float] = Field(None, gt=0)
    initial_height: Optional[float] = Field(None, gt=0)
    growth_rate: Optional[float] = Field(None, gt=0)
    bloom_season: Optional[str] = Field(None, max_length=100)

class PlantRecord(PlantBase):
    """Plant model with ID and timestamps"""
    id: int = Field(..., description="Plant ID")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    class Config:
        from_attributes = True
