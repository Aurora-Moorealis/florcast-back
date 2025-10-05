from pydantic import BaseModel
from typing import List, Optional


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


class Datum(BaseModel):
    id: Optional[int] = None
    common_name: str = ''
    scientific_name: List[str] = []
    other_name: Optional[List[str]] = None
    family: Optional[str] = None
    hybrid: Optional[str] = None
    authority: Optional[str] = None
    subspecies: Optional[str] = None
    cultivar: Optional[str] = None
    variety: Optional[str] = None
    species_epithet: Optional[str] = None
    genus: Optional[str] = None
    default_image: Optional[DefaultImage] = None


class PerenualSpeciesRequest(BaseModel):
    data: List[Datum] = []
    to: Optional[int] = None
    per_page: Optional[int] = None
    current_page: Optional[int] = None
    perenual_species_request_from: Optional[int] = None
    last_page: Optional[int] = None
    total: Optional[int] = None
