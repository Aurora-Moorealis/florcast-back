from typing import List, Optional
from datetime import datetime
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from app.models import (
    PerenualPlantDetail,
    Plant
)
import json, requests, datetime
from . import (
    PerenualSpeciesRequest,
    APIs,
    API,
    Datum
)
from app import utils
from typing import Any

class PlantService:
    """Service for managing plants (in-memory storage for demonstration)"""
    
    plants: List[Plant] = []
    
    def __init__(self):
        pass
    
    @staticmethod
    def get_plants() -> list[Plant]:
        
        with open('data/examples/plants_data.json') as file:
            
            data: list[Plant] = json.loads(file.read())
            
            return data
    
    @staticmethod
    def get_plants_prediction() -> PerenualSpeciesRequest:
        
        raw_request = API.get_json(
                APIs.PERENUAL.value,
                'species-list',
                {
                    'key': 'sk-OpS168e21d7d62e7812687'
                },
                {
                    'page': 1
                }
            )
        
        request: PerenualSpeciesRequest = PerenualSpeciesRequest(
            **raw_request
        )

        return request

    @staticmethod
    def search_plant_by_scientific_name(scientific_name: str, return_first_if_not_exists: bool = False) -> Optional[Datum]:
        """Search for a plant by its scietific_name name"""
        
        raw_request = API.get_json(
            APIs.PERENUAL.value,
            'species-list',
            {
                'key': 'sk-OpS168e21d7d62e7812687',
                'q': scientific_name
            },
            {
                'page': 1
            }
        )
        
        perenual_request: PerenualSpeciesRequest = PerenualSpeciesRequest(**raw_request)
        
        if not perenual_request.data:
            return
        
        for plant in perenual_request.data:
            
            if not plant:
                continue
            
            if plant.scientific_name[0] == scientific_name:
                return plant
        
        if return_first_if_not_exists:
            return perenual_request.data[0]
        
        return None
    
    @staticmethod
    def get_prediction(flower: Plant) -> Optional[dict[str, Any]|float]:
        """Get plant prediction from Perenual API and GLOBE based on flower data"""
        
        specie = PlantService.search_plant_by_scientific_name(flower.scientific_name[0])
        
        plant_detail: Optional[PerenualPlantDetail] = None
        
        if specie:
            raw_request = API.get_json(
                APIs.PERENUAL.value,
                'species',
                {
                    'key': 'sk-OpS168e21d7d62e7812687',
                    'id': specie.id
                }
            )

            plant_detail = PerenualPlantDetail(**raw_request)
        
            if utils.current_season() not in plant_detail.flowering_season:
                return {
                    **plant_detail.dict(),
                    'growth_percentage': 0,
                    'message': 'Not in blooming season'
                }
        
        today_date = datetime.datetime.now()
        start_date = today_date - datetime.timedelta(days=30)
        protocols: list[str] = [
            'vegatation_covers',
            'surface_temperatures',
            'precipitations'
        ]
        
        default_params = {
            'group': 'public-api',
            'protocols': ','.join(protocols),
            'startdate': start_date.strftime('%Y-%m-%d'),
            'enddate': today_date.strftime('%Y-%m-%d'),
            'geojson': True,
            'sample': False,
        }
        
        # Prepare request data
        globe_data = json.loads(
            requests.get(
                f'{APIs.GLOBE.value}measurement/protocol/measureddate/lat/lon/',
                params={
                    **default_params,
                    'datefield': 'measuredDate',
                    'minlat': flower.location.coords.latitude-10,
                    'maxlat': flower.location.coords.latitude+10,
                    'minlon': flower.location.coords.longitude-10,
                    'maxlon': flower.location.coords.longitude+10
                }
            ).text
        )
        
        if globe_data['features']:
            
            unique_protocols = {}
            
            for feature in globe_data.get("features", []):
                protocol = feature["properties"].get("protocol")
            
                if protocol not in unique_protocols:
                    unique_protocols[protocol] = feature
            
            final_values_protocols = {}
            
            for key, value in unique_protocols.items():
                
                if key == 'precipitation':
                    final_values_protocols[key] = value['properties'].get('precipitationsLiquidAccumulation')
                
                if key == 'surface_temperature':
                    final_values_protocols[key] = value['properties'].get('surfacetemperaturesAverageSurfaceTemperatureC')
                
                if key == 'vegetation_cover':
                    final_values_protocols[key] = value['properties'].get('vegatationcoversGroundCoverGreenPercent')
                
            return {
                **flower.dict(),
                'growth_percentage': utils.calculate_growth_percentage(flower, plant_detail, final_values_protocols) if plant_detail else None
            }
        
        if globe_data['results']:
            
            unique_protocols = {}
            
            for feature in globe_data.get("results", []):
                protocol = feature.get("protocol")
            
                if protocol not in unique_protocols:
                    unique_protocols[protocol] = feature
            
            final_values_protocols = {}
            
            for key, value in unique_protocols.items():
                
                if key == 'precipitation':
                    final_values_protocols[key] = value['data'].get('precipitationsLiquidAccumulation')
                
                if key == 'surface_temperature':
                    final_values_protocols[key] = value['data'].get('surfacetemperaturesAverageSurfaceTemperatureC')
                
                if key == 'vegetation_cover':
                    final_values_protocols[key] = value['data'].get('vegatationcoversGroundCoverGreenPercent')
                
            return {
                **flower.dict(),
                'growth_percentage':utils.calculate_growth_percentage(flower, plant_detail, final_values_protocols) if plant_detail else None
            }
        
        # if not globe_data['features']:
        #     country = utils.get_country(flower.latitude, flower.longitude)
            
        #     globe_data = json.loads(
        #         requests.get(
        #             f'{APIs.GLOBE.value}measurement/protocol/measureddate/country/',
        #             params={
        #                 **default_params,
        #                 'countrycode': country
        #             }
        #         ).text
        #     )
        
        # if not globe_data['features']:
        #     globe_data = json.loads(
        #         requests.get(
        #             f'{APIs.GLOBE.value}measurement/',
        #             params={
        #                 **default_params,
        #                 'datefield': 'measuredDate',
        #             }
        #         ).text
        #     )
        
        # if not globe_data['features']:
        #     return None

        # unique_protocols = {}
        
        # for feature in globe_data.get("features", []):

        #     protocol = feature["properties"].get("protocol")
            
        #     if protocol not in unique_protocols:
        #         unique_protocols[protocol] = feature
        
