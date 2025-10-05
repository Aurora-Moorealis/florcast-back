from typing import Any
import requests, json

class API:
    
    def __init__(self, url: str):
        self.url = url
    
    @staticmethod
    def request_json(method: str, url: str, endpoint: str, params: dict[str, Any] = {}, body: dict[str, Any] = {}) -> dict[str, Any]:
        
        data = requests.request(method, f'{url}{endpoint}', params=params, data=body).text
        
        print(data)
        return json.loads(data)
    
    @staticmethod
    def get(url: str, endpoint: str, params: dict[str, Any] = {}, headers: dict[str, Any] = {}, body: dict[str, Any] = {}):
        return requests.get(url=f'{url}{endpoint}', params=params, headers=headers, data=body).text
    
    @staticmethod
    def get_json(url: str, endpoint: str, params: dict[str, Any] = {}, body: dict[str, Any] = {}):
        return json.loads(API.get(url, endpoint, params))