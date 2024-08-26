import pprint
import openrouteservice
import os
import json
import random
from dotenv import load_dotenv
from flask import Flask, render_template_string, render_template
import folium
from misc.models import Graph

# Load the environment variables
load_dotenv()

# Retrieve the OpenRouteService API token
TOKEN = os.getenv('OPEN_SERVICE_API')
client = openrouteservice.Client(key=TOKEN)

# Function to select a random parking space
def choose_random_parking_space(parking_data):
    return random.choice(parking_data)

def calculate_route_from_point_to_main(start_coords, main_location):
    # Convert the start coordinates to the format expected by the openrouteservice client
    start_coords_formatted = [start_coords[1], start_coords[0]]  # (longitude, latitude)
    main_coords_formatted = [main_location["y"], main_location["x"]]  # (longitude, latitude)

    # Calculate the directions
    route_coords = [start_coords_formatted, main_coords_formatted]
    res = client.directions(coordinates=route_coords, profile='driving-car')
    return res


# Function to create a map with markers for the route and parking spaces
def create_map(data, start_coords):
    m = folium.Map(location=start_coords, zoom_start=17)

    parkinglot = Graph('data.json')
    parkinglot.connect_nodes()
    men = parkinglot.return_graph()
    spot_name, distance_from_ent, tgt_spot, visited = parkinglot.find_closest_available_parking() # tgt in RXSY format

    # # Assisted Dijkstras
    # tgt_spot = tgt_spot.__dict__

    # chosen_space = {
    #     'row_number': tgt_spot['row'],
    #     'space_number': tgt_spot['space'],
    #     'coordinates': {
    #         'x': tgt_spot['y_coord'],
    #         'y': tgt_spot['x_coord']
    #     }
    # }

    # # Prepare the coordinates for the line
    # line_coords = []

    # # Add markers for the 'Main' and 'Fork' intersections
    # main_intersection = next((inter for inter in data["Intersections"] if inter["name"] == "Entry"), None)
    # fork_intersection = next((inter for inter in data["Intersections"] if inter["name"] == "Intersection 1"), None)

    # if main_intersection:
    #     main_coords = main_intersection["coordinates"]
    #     folium.Marker([main_coords["x"], main_coords["y"]], tooltip="Main").add_to(m)
    #     line_coords.append([main_coords["x"], main_coords["y"]])

    # if fork_intersection:
    #     fork_coords = fork_intersection["coordinates"]
    #     folium.Marker([fork_coords["x"], fork_coords["y"]], tooltip="Fork").add_to(m)
    #     line_coords.append([fork_coords["x"], fork_coords["y"]])

    # # Determine the row number of the chosen parking space
    # chosen_row = chosen_space['row_number']
    # row_name = f"Row{chosen_row}"

    # # Add a marker for the intersection corresponding to the row of the chosen parking space
    # row_intersection = next((inter for inter in data["Intersections"] if inter["name"] == row_name), None)

    # if row_intersection:
    #     row_coords = row_intersection["coordinates"]
    #     folium.Marker([row_coords["x"], row_coords["y"]], tooltip=row_name).add_to(m)
    #     line_coords.append([row_coords["x"], row_coords["y"]])

    # # Add a marker for the chosen parking space and add its coordinate to the line
    # space_coords = chosen_space["coordinates"]
    # folium.Marker([space_coords["x"], space_coords["y"]],
    #               tooltip=f"Row: {chosen_space['row_number']}, Space: {chosen_space['space_number']}").add_to(m)
    # line_coords.append([space_coords["x"], space_coords["y"]])

    # # Draw a line connecting the points
    # folium.PolyLine(line_coords, color='blue', weight=5, opacity=0.8).add_to(m)

    # folium.TileLayer(
    #     tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    #     attr='Esri',
    #     name='Esri WorldImagery',
    #     overlay=False,
    #     control=True,
    #     detectRetina=True
    # ).add_to(m)

    # folium.LayerControl().add_to(m)

    # return m

    ###########################

    # Dijkstra
    nodes = parkinglot.return_graph()
    
    circle_group = folium.FeatureGroup(name='Spot Availability', show=True)
    lot_markers = folium.FeatureGroup(name='Lot Markers', show=True)

    for k, v in nodes:
        obj = v.__dict__
        
        if not obj['node_type'] == 'parking_spot':
            continue

        if obj['is_occupied'] == True:
            folium.Circle(location=[obj['y_coord'], obj['x_coord']], radius=1, color='red', fill=True, fill_color='red').add_to(circle_group)
        elif obj['is_occupied'] == False:
            folium.Circle(location=[obj['y_coord'], obj['x_coord']], radius=1, color='green', fill=True, fill_color='green').add_to(circle_group)

    space_coords = visited[-1]


    line_coords = []

    for node in visited:
        line_coords.append([node['y_coord'], node['x_coord']])

    # # Add a marker for the chosen parking space and add its coordinate to the line
    folium.Marker([space_coords["y_coord"], space_coords["x_coord"]],
                  tooltip=f"Row: {space_coords['row']}, Space: {space_coords['space']}",
                  icon=folium.Icon(color='orange', icon='flag')).add_to(lot_markers)
    # line_coords.append([space_coords["x"], space_coords["y"]])

    # # Draw a line connecting the points
    folium.PolyLine(line_coords, color='blue', weight=5, opacity=0.8).add_to(m)

    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Esri WorldImagery',
        overlay=False,
        control=True,
        detectRetina=True
    ).add_to(m)

    circle_group.add_to(m)
    lot_markers.add_to(m)

    folium.LayerControl().add_to(m)

    return m

def create_direction_markers(m, res):
    # Extract the geometry of the route which contains all the coordinates
    geometry = res['routes'][0]['geometry']
    
    # Decode polyline to get the list of coordinates
    # This should follow the road accurately
    coordinates = openrouteservice.convert.decode_polyline(geometry)['coordinates']
    
    # Convert the coordinates to the format expected by Folium (latitude, longitude)
    decoded_coords = [[coord[1], coord[0]] for coord in coordinates]

    directions = []

    duration = 0

    # Go through each segment and each step within that segment
    for segment in res['routes'][0]['segments']:
        duration += segment['duration']
        for step in segment['steps']:
            # Retrieve the start and end coordinates of the step
            start_index = step['way_points'][0]
            end_index = step['way_points'][1]
            start_coordinate = coordinates[start_index]
            end_coordinate = coordinates[end_index]

            # Swap the coordinates to match folium (latitude, longitude)
            start_coord_for_marker = [start_coordinate[1], start_coordinate[0]]
            end_coord_for_marker = [end_coordinate[1], end_coordinate[0]]
            
            # Create markers for the start and end points of each step
            folium.Marker(
                start_coord_for_marker,
                tooltip=step['instruction'],
                icon=folium.Icon(color='green' if start_index == 0 else 'blue', icon='info-sign')
            ).add_to(m)
            
            if start_index != end_index:  # If the step has a distance, mark the end as well
                folium.Marker(
                    end_coord_for_marker,
                    tooltip=step['instruction'],
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(m)

            directions.append(step['instruction'])

    directions.insert(0, f'ETA in {round(duration/60)} minutes')

    # Draw the polyline on the map
    folium.PolyLine(decoded_coords, color='blue', weight=5, opacity=0.8).add_to(m)
    
    # Optionally, add markers for the start and end points
    folium.Marker(
        decoded_coords[0],
        tooltip='Start',
        icon=folium.Icon(color='green', icon='play')
    ).add_to(m)

    return m, directions

app = Flask(__name__)

# Flask route to display the map
@app.route('/')
def show_map():
    # Load the data from the JSON file
    with open('data.json', 'r') as json_file:
        data = json.load(json_file)

    # Get the coordinates for the 'Main' intersection
    main_location = next(inter for inter in data["Intersections"] if inter["name"] == "Entry")["coordinates"]

    # Coordinates where the new route starts
    locations = [(40.1080572, -75.1116347), (40.1252999714912, -75.11646240727026), (40.11156531109428, -75.09302079242812)]

    start_coords = random.choice(locations)

    # Calculate the route from the start point to 'Main'
    route_to_main_res = calculate_route_from_point_to_main(start_coords, main_location)

    # Create the folium map object
    folium_map = create_map(data, start_coords)

    # Add direction markers for the route from the start point to 'Main'
    folium_map, directions = create_direction_markers(folium_map, route_to_main_res)

    # Use a simple template to serve the map HTML
    return render_template('index.html', map_html=folium_map._repr_html_(), directions=directions)


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
    
