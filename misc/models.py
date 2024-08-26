import heapq
import json
import pprint
import random
from geopy.distance import geodesic


class Node:
    def __init__(self, node_type):
        self.node_type = node_type  # Type of node ('parking_spot', 'entry', 'intersection')
        self.adjacent_nodes = []  # List to store adjacent nodes
    
    def distance_to(self, other_node):
        # Coordinates of the two nodes
        coords_1 = (self.y_coord, self.x_coord)  # latitude, longitude
        coords_2 = (other_node.y_coord, other_node.x_coord)  # latitude, longitude

        # Calculate distance
        distance = geodesic(coords_1, coords_2).meters

        return distance
    

class ParkingSpot(Node):
    def __init__(self, id, row, space, x_coord, y_coord, is_occupied=False):
        super().__init__("parking_spot")
        self.id = id
        self.row = row
        self.space = space
        self.x_coord = y_coord  # Longitude
        self.y_coord = x_coord  # Latitude
        self.is_occupied = is_occupied

class Intersection(Node):
    def __init__(self, id, x_coord, y_coord, isEntrance=False):
        super().__init__("intersection")
        self.id = id # ID for which intersection it is
        self.x_coord = x_coord  # X-coordinate of the intersection
        self.y_coord = y_coord  # Y-coordinate of the intersection

class Entry(Node):
    def __init__(self, id, x_coord, y_coord):
        super().__init__("entry")
        self.id = id # ID for which entrance it is
        self.x_coord = x_coord  # X-coordinate of the entrance
        self.y_coord = y_coord  # Y-coordinate of the entrance

class Graph():
    def __init__(self, filename):
        self.nodes = {}
        self.entry_node = None 
        self.load_from_json(filename)

    def add_node(self, node_id, node):
        if node_id in self.nodes:
            raise ValueError(f"Node with id {node_id} already exists.")
        self.nodes[node_id] = node
        if node_id == "Entry":
            self.entry_node = node

    def add_edge(self, from_node_id, to_node_id, weight):
        if from_node_id not in self.nodes or to_node_id not in self.nodes:
            raise ValueError("Both nodes must exist in the graph.")
        self.nodes[from_node_id].adjacent_nodes.append((self.nodes[to_node_id], weight))

    def connect_nodes(self):
        # Connect the entry point to Intersection 1
        if 'Entry' in self.nodes and 'Intersection 1' in self.nodes:
            entry_to_intersection_distance = self.nodes['Entry'].distance_to(self.nodes['Intersection 1'])
            self.add_edge('Entry', 'Intersection 1', entry_to_intersection_distance)

        # Connect each intersection to the next
        total_intersections = 4
        for i in range(1, total_intersections):
            from_intersection = f'Intersection {i}'
            to_intersection = f'Intersection {i + 1}'
            if from_intersection in self.nodes and to_intersection in self.nodes:
                inter_to_inter_distance = self.nodes[from_intersection].distance_to(self.nodes[to_intersection])
                self.add_edge(from_intersection, to_intersection, inter_to_inter_distance)

        # Connect parking spots to respective intersections with the correct weight
        for node_id, node in self.nodes.items():
            if node.node_type == 'parking_spot':
                row_number = int(node_id.split('R')[1].split('S')[0])
                intersection_name = self.determine_intersection(row_number)
                if intersection_name and intersection_name in self.nodes:
                    spot_to_intersection_distance = self.nodes[node_id].distance_to(self.nodes[intersection_name])
                    self.add_edge(node_id, intersection_name, spot_to_intersection_distance)
                    # Add reverse edge from intersection to parking spot
                    self.add_edge(intersection_name, node_id, spot_to_intersection_distance)

    def determine_intersection(self, row_number):
        # Define mapping of row numbers to intersections
        if row_number in [1, 2]:
            return 'Intersection 4'
        elif row_number in [3, 4]:
            return 'Intersection 3'
        elif row_number == 5:
            return 'Intersection 2'
        else:
            return None
    
    def load_from_json(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)

            # Load Parking Spots
            for spot in data['Woodland']:
                node = ParkingSpot(
                    id=f"R{spot['row_number']}S{spot['space_number']}",
                    row=spot['row_number'],
                    space=spot['space_number'],
                    x_coord=spot['coordinates']['x'],  # Latitude
                    y_coord=spot['coordinates']['y'],  # Longitude
                    is_occupied=random.choice([True, False])
                    # is_occupied=True if 4 <= spot['row_number'] <= 5 else False
                )
                self.add_node(node.id, node)

            # Load Intersections
            for intersection in data['Intersections']:
                node = Intersection(
                    id=intersection['name'],
                    x_coord=intersection['coordinates']['y'],  # Latitude
                    y_coord=intersection['coordinates']['x'],  # Longitude
                )
                self.add_node(node.id, node)
    
    def print_graph(self):
        """Prints the graph."""
        for node_id, node in self.nodes.items():
            for adj_node, weight in node.adjacent_nodes:
                print(f"Node {node_id} is connected to {adj_node.id} with weight {weight}")

    def return_graph(self):
         return self.nodes.items()
    
    #Looks for the closest parking spot
    def find_closest_available_parking(self):
        closest_parking_spot = None
        min_distance = float('inf')

        tgt_spot = None
        shortest_path = []

        for spot_id, spot in self.nodes.items():
            if spot.node_type == 'parking_spot' and not spot.is_occupied:
                distance, path = self.dijkst(spot_id)
                if distance < min_distance:
                    min_distance = distance
                    closest_parking_spot = spot_id
                    tgt_spot = spot
                    shortest_path = path

        return closest_parking_spot, min_distance, tgt_spot, shortest_path

    #Finds the distance to the target parking spot
    def dijkst(self, target_spot_id):
        start_id = self.entry_node.id

        #Makes list of all nodes and assigns a distance of inf to them
        distances = {node_id: float('inf') for node_id in self.nodes}
        distances[start_id] = 0

        previous = {node_id: None for node_id in self.nodes}
        priority_queue = [(0, start_id)] 

        while priority_queue:
            
            current_distance, current_node_id = heapq.heappop(priority_queue)
            if current_node_id == target_spot_id:
                
                path = []
                while current_node_id is not None:
                    current_node = self.nodes[current_node_id]
                    path.append(current_node.__dict__)
                    current_node_id = previous[current_node_id]
                return current_distance, path[::-1]

            if current_distance > distances[current_node_id]:
                continue

            for adjacent_node, weight in self.nodes[current_node_id].adjacent_nodes:
                distance = current_distance + weight

                if distance < distances[adjacent_node.id]:
                    distances[adjacent_node.id] = distance
                    previous[adjacent_node.id] = current_node_id
                    heapq.heappush(priority_queue, (distance, adjacent_node.id))

                if adjacent_node.id == target_spot_id:
                    break
        path = []
        current_node_id = target_spot_id  # Start from the target spot
        while current_node_id is not None:
            path.append(current_node_id)
            current_node_id = previous[current_node_id]
        return float('inf'), path[::-1]


if __name__ == '__main__':
    parkinglot = Graph('data.json')
    parkinglot.connect_nodes()
    # parkinglot.print_graph()
    tgt, distance_from_ent, tgt_spot, visited_nodes = parkinglot.find_closest_available_parking() # tgt in RXSY format

    tgt = tgt.split('S')
    tgt_row = int(tgt[0].split('R')[1])
    tgt_space = int(tgt[1])

    print(tgt_row, tgt_space, distance_from_ent, visited_nodes)
    pprint.pprint(tgt_spot.__dict__)