from app import Point, Location, Plant
# UNUSED

# def convert_to_plant(data: dict) -> Plant:
#     """Convert a raw flower dictionary into a validated Plant model."""
    
#     max_deg = lambda x: min(max(x, -90), 90)
#     location = Location(
#         country_code=data.get("country_code"),
#         location_name=data.get("location_name"),
#         coords=Point(
#             latitude=max_deg(data.get("latitude")),
#             longitude=max_deg(data.get("longitude"))
#         )
#     )

#     return Plant(
#         id=data["id"],
#         scientific_name=data["scientific_name"],
#         common_name=data.get("common_name"),
#         description=data.get("description"),
#         max_height=data.get("max_height"),
#         initial_height=data.get("initial_height"),
#         temperature_to_grow=data.get("temperature_to_grow"),
#         growth_rate=data.get("growth_rate"),
#         bloom_season=data.get("bloom_season"),
#         created_at=data.get("created_at"),
#         updated_at=data.get("updated_at"),
#         planting_date=data.get("planting_date"),
#         location=location
#     )

# with open('data/examples/plants_data.json') as file:
#     import json
#     raw_data = json.load(file)
#     plants = [convert_to_plant(item) for item in raw_data]
    
#     with open('data/examples/converted_plants_data.json', 'w') as outfile:
#         json.dump([plant.dict() for plant in plants], outfile, indent=4, default=str)