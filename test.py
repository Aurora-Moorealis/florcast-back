# import requests

# params = {
#     "taxon_id": 47126,  # example: 'Magnoliopsida' or use species id
#     "swlat": 18.0, "swlng": -71.9, "nelat": 19.2, "nelng": -68.0, # bbox
#     "per_page": 50
# }
# r = requests.get("https://api.inaturalist.org/v1/observations", params=params)
# data = r.json()
# for obs in data.get("results", []):
#     print(obs.get("taxon", {}).get("name"), obs.get("latitude"), obs.get("longitude"))