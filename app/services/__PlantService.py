from typing import List, Optional
from datetime import datetime
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from app.models._Plant import Plant, PlantCreate, PlantUpdate
import json
from . import PlantBase

class PlantService:
    """Service for managing plants (in-memory storage for demonstration)"""
    
    plants: List[Plant] = []
    
    def __init__(self):
        pass
    
    def get_plants(self) -> list[PlantBase]:
        
        with open('../../data/examples/plants_data.json') as file:
            
            data: list[PlantBase] = json.loads(file.read())
            
            return data
            
            
    