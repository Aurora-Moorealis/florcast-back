from typing import List, Optional, Literal
from pydantic import BaseModel
from app.ptypes import Station

GhrowthRate = Literal['HIGH', 'MEDIUM', 'LOW']

class Dimensions(BaseModel):
    type: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    unit: Optional[str] = None


class WateringBenchmark(BaseModel):
    value: Optional[str] = None  # changed to string since "5-7" isn't numeric
    unit: Optional[str] = None


class PlantPart(BaseModel):
    part: Optional[str] = None
    color: Optional[List[str]] = None


class PruningCount(BaseModel):
    amount: Optional[int] = None
    interval: Optional[str] = None


class Hardiness(BaseModel):
    min: Optional[str] = None
    max: Optional[str] = None


class HardinessLocation(BaseModel):
    full_url: Optional[str] = None
    full_iframe: Optional[str] = None


class DefaultImage(BaseModel):
    image_id: Optional[int] = None
    license: Optional[int] = None
    license_name: Optional[str] = None
    license_url: Optional[str] = None
    original_url: Optional[str] = None
    regular_url: Optional[str] = None
    medium_url: Optional[str] = None
    small_url: Optional[str] = None
    thumbnail: Optional[str] = None


class OtherImage(BaseModel):
    image_id: Optional[int] = None
    license: Optional[int] = None
    license_name: Optional[str] = None
    license_url: Optional[str] = None
    original_url: Optional[str] = None
    regular_url: Optional[str] = None
    medium_url: Optional[str] = None
    small_url: Optional[str] = None
    thumbnail: Optional[str] = None


class WateringTemperature(BaseModel):
    unit: Optional[str] = None
    min: Optional[float] = None
    max: Optional[float] = None


class PhLevel(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None


class SunlightDuration(BaseModel):
    min: Optional[str] = None
    max: Optional[str] = None
    unit: Optional[str] = None


class PerenualPlantDetail(BaseModel):
    id: int
    common_name: Optional[str] = None
    scientific_name: Optional[List[str]] = None
    other_name: Optional[List[str]] = None
    family: Optional[str] = None
    origin: Optional[str] = None
    type: Optional[str] = None
    dimensions: Optional[Dimensions] = None
    cycle: Optional[str] = None
    watering: Optional[str] = None
    watering_general_benchmark: Optional[WateringBenchmark] = None
    plant_anatomy: Optional[List[PlantPart]] = None
    sunlight: Optional[List[str]] = None
    pruning_month: Optional[List[str]] = None
    pruning_count: Optional[PruningCount] = None
    seeds: Optional[int] = None
    attracts: Optional[List[str]] = None
    propagation: Optional[List[str]] = None
    hardiness: Optional[Hardiness] = None
    hardiness_location: Optional[HardinessLocation] = None
    flowers: Optional[bool] = None
    flowering_season: list[Station] = []
    soil: Optional[List[str]] = None
    pest_susceptibility: Optional[str] = None
    cones: Optional[bool] = None
    fruits: Optional[bool] = None
    edible_fruit: Optional[bool] = None
    fruiting_season: Optional[str] = None
    harvest_season: Optional[str] = None
    harvest_method: Optional[str] = None
    leaf: Optional[bool] = None
    edible_leaf: Optional[bool] = None
    growth_rate: GhrowthRate = 'LOW'
    maintenance: Optional[str] = None
    medicinal: Optional[bool] = None
    poisonous_to_humans: Optional[bool] = None
    poisonous_to_pets: Optional[bool] = None
    drought_tolerant: Optional[bool] = None
    salt_tolerant: Optional[bool] = None
    thorny: Optional[bool] = None
    invasive: Optional[bool] = None
    rare: Optional[bool] = None
    tropical: Optional[bool] = None
    cuisine: Optional[bool] = None
    indoor: Optional[bool] = None
    care_level: Optional[str] = None
    description: Optional[str] = None
    default_image: Optional[DefaultImage] = None
    other_images: Optional[List[OtherImage]] = None
    xWateringQuality: Optional[List[str]] = None
    xWateringPeriod: Optional[List[str]] = None
    xWateringAvgVolumeRequirement: Optional[List[str]] = None
    xWateringDepthRequirement: Optional[List[str]] = None
    xWateringBasedTemperature: Optional[WateringTemperature] = None
    xWateringPhLevel: Optional[PhLevel] = None
    xSunlightDuration: Optional[SunlightDuration] = None
