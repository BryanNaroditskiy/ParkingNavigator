from flask import Flask, render_template_string
import folium
from geopy.distance import geodesic
from geopy.distance import distance
import heapq
import json

app = Flask(__name__)


def create_map(data):
    m = folium.Map(location=[40.117207, -75.111677], zoom_start=25)

    # Get the points from the same row (assuming 'row_number' is a key in your data)
    same_row_points = [spot for spot in data['Woodland'] if spot['row_number'] == 1]  # Adjust row number as needed

    # Sort the points by 'space_number' to get them in order
    same_row_points.sort(key=lambda x: x['space_number'])

    # Add markers for the first and spot number 13 in the row
    for point in [same_row_points[0], same_row_points[12]]:
        coords = point['coordinates']
        folium.Marker([coords['x'], coords['y']],
                      tooltip=f"Row: {point['row_number']}, Space: {point['space_number']}").add_to(m)

    # Draw a line between the first and spot number 13
    folium.PolyLine(
        locations=[(same_row_points[0]['coordinates']['x'], same_row_points[0]['coordinates']['y']),
                   (same_row_points[12]['coordinates']['x'], same_row_points[12]['coordinates']['y'])],
        color='blue',
        weight=5,
        opacity=0.5
    ).add_to(m)

    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Esri WorldImagery',
        overlay=False,
        control=True,
        detectRetina=True
    ).add_to(m)

    # Add a layer control panel to the map
    folium.LayerControl().add_to(m)

    return m

@app.route('/')
def show_map():
    # Load your JSON data here
    with open('data.json', 'r') as json_file:
        data = json.load(json_file)

    # Create the folium map object
    folium_map = create_map(data)

    # Render the map as an HTML string
    map_html = folium_map._repr_html_()

    # Use a simple template to serve the map HTML
    return render_template_string('<html><body>{{ map_html|safe }}</body></html>', map_html=map_html)

if __name__ == '__main__':
    #app.run(debug=True, port=5000)
    parkinglot = Graph('data.json')
    parkinglot.connect_nodes()
    parkinglot.print_graph()
    print(parkinglot.find_closest_available_parking())