from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from app.models._Plant import Plant, PlantCreate, PlantUpdate, PlantBase
from app.services.__PlantService import PlantService

router = APIRouter()
plant_service = PlantService()


@router.get("/plants", response_model=List[PlantBase])
async def get_plants() -> List[PlantBase]:
    """Get all plants"""
    return plant_service.get_plants()

@router.get("/predictions")
async def get_predictions() -> List[PlantBase]:
    "Get all predictions"
    
    
    answer = PlantService.request_plants_prediction()
    print(answer)
    return []