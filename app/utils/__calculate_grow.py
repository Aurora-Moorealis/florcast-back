from app.models import PerenualPlantDetail, GhrowthRate, PlantBase
from typing import Any

growth_to_number: dict[GhrowthRate, int] = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 4,
}

def calculate_growth_percentage(plant: PlantBase, plant_detail: PerenualPlantDetail, globe_data: dict[str, Any]) -> float:
    """
    Calculate the growth percentage of a plant based on its details and weather data.
    
    Args:
        plant_detail (PerenualPlantDetail): The detailed information about the plant.
        weather_data (dict): The weather data containing temperature, humidity, and sunlight information.

    Returns:
        float: The calculated growth percentage of the plant.
    """
    
    weights: dict[str, float] = {
        'temperature': 0.2,
        'precipitation': 0.3,
        'vegetation_cover': 0.4
    }
    
    
    height = plant.initial_height or 0
    r = growth_to_number[plant_detail.growth_rate]
    
    precipitation = globe_data.get('precipitation')
    temperature = globe_data.get('surface_temperature')
    vegetation_cover = globe_data.get('vegatation_cover')

    g = (weights['precipitation']*precipitation + weights['temperature']*temperature + weights['vegetation_cover']*vegetation_cover)/sum(weights.values()) if precipitation and temperature and vegetation_cover else 0
    k = 0.01
    e = 5

    return height*(1+k*g)+e