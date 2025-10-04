from typing import List, Optional
from datetime import datetime
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from app.models.plant import Plant, PlantCreate, PlantUpdate


class PlantService:
    """Service for managing plants (in-memory storage for demonstration)"""
    
    def __init__(self):
        self.plants: List[Plant] = []
        self.next_id: int = 1
        
        # Add some sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample plant data"""
        sample_plants = [
            PlantCreate(
                scientific_name="Rosa rubiginosa",
                common_name="Sweet Briar Rose",
                family="Rosaceae",
                description="A species of wild rose with fragrant foliage and pink flowers",
                latitude=51.5074,
                longitude=-0.1278,
                location_name="London, UK",
                height_cm=200.0,
                bloom_season="Spring-Summer",
            ),
            PlantCreate(
                scientific_name="Sequoiadendron giganteum",
                common_name="Giant Sequoia",
                family="Cupressaceae",
                description="One of the largest and longest-living trees on Earth",
                latitude=36.4864,
                longitude=-118.5658,
                location_name="Sequoia National Park, USA",
                height_cm=8000.0,
                bloom_season="Winter-Spring",
            ),
            PlantCreate(
                scientific_name="Lavandula angustifolia",
                common_name="English Lavender",
                family="Lamiaceae",
                description="Aromatic flowering plant widely cultivated for its fragrant flowers",
                latitude=43.6108,
                longitude=3.8767,
                location_name="Montpellier, France",
                height_cm=60.0,
                bloom_season="Summer",
            ),
        ]
        for plant_data in sample_plants:
            self.create_plant(plant_data)
    
    def get_all_plants(self) -> List[Plant]:
        """Get all plants"""
        return self.plants
    
    def get_plant_by_id(self, plant_id: int) -> Optional[Plant]:
        """Get a plant by ID"""
        for plant in self.plants:
            if plant.id == plant_id:
                return plant
        return None
    
    def create_plant(self, plant_data: PlantCreate) -> Plant:
        """Create a new plant"""
        new_plant = Plant(
            id=self.next_id,
            **plant_data.model_dump(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.plants.append(new_plant)
        self.next_id += 1
        return new_plant
    
    def update_plant(self, plant_id: int, plant_update: PlantUpdate) -> Optional[Plant]:
        """Update an existing plant"""
        plant = self.get_plant_by_id(plant_id)
        if not plant:
            return None
        
        update_data = plant_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(plant, field, value)
        
        plant.updated_at = datetime.now()
        return plant
    
    def delete_plant(self, plant_id: int) -> bool:
        """Delete a plant"""
        plant = self.get_plant_by_id(plant_id)
        if not plant:
            return False
        
        self.plants.remove(plant)
        return True
    
    def get_plants_dataframe(self) -> pd.DataFrame:
        """Get plants as pandas DataFrame for data analysis"""
        if not self.plants:
            return pd.DataFrame()
        
        data = [plant.model_dump() for plant in self.plants]
        return pd.DataFrame(data)
    
    def get_statistics(self) -> dict:
        """Get statistical analysis of plants data"""
        df = self.get_plants_dataframe()
        
        if df.empty:
            return {"message": "No data available"}
        
        stats = {
            "total_plants": len(self.plants),
            "endangered_count": int(df['is_endangered'].sum()) if 'is_endangered' in df else 0,
            "families_count": len(df['family'].unique()) if 'family' in df else 0,
            "average_height_cm": float(df['height_cm'].mean()) if 'height_cm' in df and not df['height_cm'].isna().all() else None,
            "height_stats": {
                "min": float(df['height_cm'].min()) if 'height_cm' in df and not df['height_cm'].isna().all() else None,
                "max": float(df['height_cm'].max()) if 'height_cm' in df and not df['height_cm'].isna().all() else None,
                "std": float(df['height_cm'].std()) if 'height_cm' in df and not df['height_cm'].isna().all() else None,
            }
        }
        
        return stats
    
    def find_plants_near_location(self, latitude: float, longitude: float, radius_km: float = 100) -> List[dict]:
        """Find plants within a certain radius from a location"""
        target_location = (latitude, longitude)
        nearby_plants = []
        
        for plant in self.plants:
            if plant.latitude is not None and plant.longitude is not None:
                plant_location = (plant.latitude, plant.longitude)
                distance = geodesic(target_location, plant_location).kilometers
                
                if distance <= radius_km:
                    nearby_plants.append({
                        "plant": plant,
                        "distance_km": round(distance, 2)
                    })
        
        # Sort by distance
        nearby_plants.sort(key=lambda x: x['distance_km'])
        return nearby_plants
