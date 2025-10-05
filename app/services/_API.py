from typing import Any
import requests, json

class API:
    
    def __init__(self, url: str):
        self.url = url
    
    @staticmethod
    def get(url: str, endpoint: str, params: list[Any] = [], headers: dict[str, Any] = {}):
        return requests.get(url=f'{url}{endpoint}', params=params, headers=headers).text
    
    @staticmethod
    def get_json(url: str, endpoint: str, params: list[Any] = []):
        return json.loads(API.get(url, endpoint, params))