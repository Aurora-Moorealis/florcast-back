from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from app.models._Plant import Plant, PlantCreate, PlantUpdate
from app.services.__PlantService import PlantService

router = APIRouter()
plant_service = PlantService()


@router.get("/plants", response_model=List[Plant])
async def get_plants():
    """Get all plants"""
    return plant_service.get_plants()

