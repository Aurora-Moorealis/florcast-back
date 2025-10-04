from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PlantBase(BaseModel):
    """Base plant model"""
    scientific_name: str = Field(..., min_length=1, max_length=200, description="Scientific name of the plant")
    common_name: str = Field(..., min_length=1, max_length=100, description="Common name of the plant")
    family: str = Field(..., min_length=1, max_length=100, description="Plant family")
    description: Optional[str] = Field(None, max_length=1000, description="Plant description")
    
    # Geographic data
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude of observation")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude of observation")
    location_name: Optional[str] = Field(None, max_length=200, description="Location name")
    
    # Plant characteristics
    height_cm: Optional[float] = Field(None, gt=0, description="Average height in centimeters")
    bloom_season: Optional[str] = Field(None, max_length=100, description="Blooming season")


class PlantCreate(PlantBase):
    """Model for creating a plant"""
    pass


class PlantUpdate(BaseModel):
    """Model for updating a plant"""
    scientific_name: Optional[str] = Field(None, min_length=1, max_length=200)
    common_name: Optional[str] = Field(None, min_length=1, max_length=100)
    family: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    height_cm: Optional[float] = Field(None, gt=0)
    bloom_season: Optional[str] = Field(None, max_length=100)


class Plant(PlantBase):
    """Plant model with ID and timestamps"""
    id: int = Field(..., description="Plant ID")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    class Config:
        from_attributes = True
