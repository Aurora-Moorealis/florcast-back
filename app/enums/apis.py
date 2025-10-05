from enum import Enum

class APIs(Enum, str):
    GLOBE = 'https://api.globe.gov/search/v1/{}?group=public-api'
    PERENUAL = 'https://perenual.com/api/v2/{}?key={}'
    