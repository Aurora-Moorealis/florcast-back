from typing import List, Optional
from datetime import datetime
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from app.models._Plant import Plant, PlantCreate, PlantUpdate
import json
from . import PlantBase, PerenualSpeciesRequest, APIs, API
import requests

class PlantService:
    """Service for managing plants (in-memory storage for demonstration)"""
    
    plants: List[Plant] = []
    
    def __init__(self):
        pass
    
    @staticmethod
    def get_plants() -> list[PlantBase]:
        
        with open('../../data/examples/plants_data.json') as file:
            
            data: list[PlantBase] = json.loads(file.read())
            
            return data
    
    @staticmethod
    def request_plants_prediction():
        
        request: PerenualSpeciesRequest = PerenualSpeciesRequest(
            **API.get_json(
                APIs.PERENUAL.value,
                'species-list',
                {
                    'key': 'sk-OpS168e21d7d62e7812687'
                },
                {
                    'page': 1
                }
            )
        )
        
        print(json.dumps(request, indent=4))
        
        return request