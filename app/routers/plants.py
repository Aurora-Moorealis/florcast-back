from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from app.models.plant import Plant, PlantCreate, PlantUpdate
from app.services.plant_service import PlantService

router = APIRouter()
plant_service = PlantService()


@router.get("/plants", response_model=List[Plant])
async def get_plants():
    """Get all plants"""
    return plant_service.get_all_plants()


@router.get("/plants/{plant_id}", response_model=Plant)
async def get_plant(plant_id: int):
    """Get a specific plant by ID"""
    plant = plant_service.get_plant_by_id(plant_id)
    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plant with id {plant_id} not found"
        )
    return plant


@router.post("/plants", response_model=Plant, status_code=status.HTTP_201_CREATED)
async def create_plant(plant: PlantCreate):
    """Create a new plant"""
    return plant_service.create_plant(plant)


@router.put("/plants/{plant_id}", response_model=Plant)
async def update_plant(plant_id: int, plant_update: PlantUpdate):
    """Update an existing plant"""
    plant = plant_service.update_plant(plant_id, plant_update)
    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plant with id {plant_id} not found"
        )
    return plant


@router.delete("/plants/{plant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plant(plant_id: int):
    """Delete a plant"""
    success = plant_service.delete_plant(plant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plant with id {plant_id} not found"
        )
    return None


@router.get("/plants/statistics/summary")
async def get_statistics():
    """Get statistical analysis of plants data"""
    return plant_service.get_statistics()


@router.get("/plants/search/nearby")
async def find_nearby_plants(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    radius_km: float = Query(100, gt=0, le=10000, description="Search radius in kilometers")
):
    """Find plants near a specific location"""
    results = plant_service.find_plants_near_location(latitude, longitude, radius_km)
    return {
        "location": {"latitude": latitude, "longitude": longitude},
        "radius_km": radius_km,
        "count": len(results),
        "plants": results
    }
