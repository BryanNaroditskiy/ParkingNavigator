import openrouteservice
import os
import json
from dotenv import load_dotenv
import random
load_dotenv()

TOKEN = os.getenv('OPEN_SERVICE_API')
client = openrouteservice.Client(key=TOKEN)

def calculate_total_distance(main_location, fork_location, parking_space_location, waypoints):
    main_lon, main_lat = main_location["y"], main_location["x"]
    fork_lon, fork_lat = fork_location["y"], fork_location["x"]
    space_lon, space_lat = parking_space_location["y"], parking_space_location["x"]

    # Rydal coordinates
    rydal_cords = [-75.112045, 40.108015]
    coords_rydal_to_main = [rydal_cords, [main_lon, main_lat]]
    res_rydal_to_main = client.directions(coordinates=coords_rydal_to_main, profile='driving-car')
    distance_rydal_to_main = res_rydal_to_main['routes'][0]['segments'][0]['distance']

    coords = [[rydal_cords[0], rydal_cords[1]], [main_lon, main_lat], [fork_lon, fork_lat], [space_lon, space_lat]]
    res = client.directions(coordinates=coords, profile='driving-car')
    total_distance = res['routes'][0]['segments'][0]['distance']
    total_duration = res['routes'][0]['segments'][0]['duration']

    return  total_distance, total_duration, parking_space_location

def choose_random_parking_space(parking_data):
    random_space = random.choice(parking_data)
    return random_space

def main():
    with open("data.json", "r") as file:
        data = json.load(file)
    
    main_location = data["Intersections"][0]["coordinates"]
    fork_location = data["Intersections"][1]["coordinates"]
    parking_space_data = data.get("Woodland", [{"coordinates": {"y": 0, "x": 0}}])
    chosen_space = choose_random_parking_space(parking_space_data)
    #waypoints
    waypoints = {item["name"]: item["coordinates"] for item in data["Intersections"] if "Row" in item["name"]}
    row_name = f"Row{chosen_space.get('row_number', '0')}"
    if row_name in waypoints:
        waypoint_coordinates = waypoints[row_name]
    else:
        print(f"Error: Waypoint {row_name} not found.")
        exit()
    
    total_distance, total_duration, parking_space_location = calculate_total_distance(
        main_location, fork_location, chosen_space["coordinates"], waypoints)
    
    print(f"Total Distance: {total_distance * 0.000621371:.2f} miles")
    print(f"Total Duration: {total_duration / 60:.2f} minutes")
    print(f"Chosen Waypoint: {row_name}")
    print(f"Chosen Parking Space Row: {chosen_space.get('row_number', 'N/A')}")
    print(f"Chosen Parking Space Number: {chosen_space.get('space_number', 'N/A')}")
    print(f"Parking Space Coordinates: {parking_space_location['y']}, {parking_space_location['x']}")
    print()

if __name__ == "__main__":
    main()