from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Any
from app.models._Plant import Plant
from app.services.__PlantService import PlantService
from app.models import PerenualSpeciesRequest, Datum

router = APIRouter()
plant_service = PlantService()

@router.get("/plants", response_model=List[Plant])
async def get_plants() -> List[Plant]:
    """Get all plants"""
    return plant_service.get_plants()

@router.get("/plant")
async def get_plant(plant_id: int = Query(..., ge=1)) -> Plant:
    """Get a plant by its ID"""
    plants = plant_service.get_plants()
    
    for plant in plants:
        if plant == plant_id:
            return plant
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Plant with ID {plant_id} not found"
    )

@router.get("/predictions")
async def get_predictions() -> List[Datum]:
    "Get all predictions"
    
    
    answer = PlantService.get_plants_prediction()
    
    if len(answer.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No predictions found"
        )
    
    return answer.data

@router.get('/predict')
async def predict_growth(scientific_name: str = Query(...)) -> Any:
    
    pass