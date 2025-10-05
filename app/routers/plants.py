from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Any
from app.models._Plant import Plant, PlantCreate, PlantUpdate, PlantBase
from app.services.__PlantService import PlantService
from app.models import PerenualSpeciesRequest, Datum

router = APIRouter()
plant_service = PlantService()


@router.get("/plants", response_model=List[PlantBase])
async def get_plants() -> List[PlantBase]:
    """Get all plants"""
    return plant_service.get_plants()

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
    
    plant = PlantService.search_plant_by_scientific_name(scientific_name, True)
    
    return PlantService.get_prediction(plant) # type: ignore