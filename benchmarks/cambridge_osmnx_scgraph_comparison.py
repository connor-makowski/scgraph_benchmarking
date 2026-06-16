import osmnx as ox
from scgraph import GeoGraph
import time
import requests
from pamda import pamda

keys = pamda.read_json('keys.json')
google_api_key = keys.get('google_api_key')


def get_google_dist_and_time(coord1, coord2):
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": google_api_key,
        "X-Goog-FieldMask": "routes.duration,routes.distanceMeters"
    }
    body = {
        "origin": {"location": {"latLng": {"latitude": coord1[0], "longitude": coord1[1]}}},
        "destination": {"location": {"latLng": {"latitude": coord2[0], "longitude": coord2[1]}}},
        "travelMode": "BICYCLE"
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None, None
    data = response.json()
    route = data["routes"][0]
    distance_km = route["distanceMeters"] / 1000
    time_seconds = int(route["duration"].rstrip("s"))
    return distance_km, time_seconds

# Pull the bike network for Somerville and Cambridge, MA
G = ox.graph_from_place(
    ['Somerville, Massachusetts, USA', 'Cambridge, Massachusetts, USA'],
    network_type='bike'
)

# Add bike speeds and compute travel times (in seconds) for each edge
G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)


# 8 Common Locations in Somerville and Cambridge, MA
locations = {
    'Central Square':      (42.3655, -71.1038),
    'Davis Square':        (42.3967, -71.1220),
    'Porter Square':       (42.3884, -71.1191),
    'Union Square':        (42.3876, -71.0995),
    'Inman Square':        (42.3730, -71.0995),
    'MIT':                 (42.3601, -71.0942),
    'Tufts University':    (42.4075, -71.1190),
    'Cambridge City Hall': (42.3666, -71.1056),
}

# Helper: sum a single edge attribute along a path
def route_attr_sum(G, path, attr):
    return sum(G[u][v][0].get(attr, 0) for u, v in zip(path[:-1], path[1:]))


# Create GeoGraphs from the OSMnx graph for time and distance calculations
geograph_time     = GeoGraph.load_from_osmnx_graph(G, weight_key='travel_time')
geograph_distance = GeoGraph.load_from_osmnx_graph(G, weight_key='length')


data = []

for loc1, coord1 in locations.items():
    for loc2, coord2 in locations.items():
        if loc1 == loc2:
            continue

        origin      = {'latitude': coord1[0], 'longitude': coord1[1]}
        destination = {'latitude': coord2[0], 'longitude': coord2[1]}

        # --- scgraph: shortest path by time ---
        start_time = time.time()
        scgraph_time_result = geograph_time.get_shortest_path(
            origin_node=origin, destination_node=destination, output_path=True
        )
        scgraph_time_optimized_time_seconds  = scgraph_time_result['length']
        scgraph_time_optimized_distance_km   = geograph_distance.get_path_weight(scgraph_time_result)
        scgraph_time_optimized_duration      = time.time() - start_time

        # --- scgraph: shortest path by distance ---
        start_time = time.time()
        scgraph_dist_result = geograph_distance.get_shortest_path(
            origin_node=origin, destination_node=destination, output_path=True
        )
        scgraph_distance_optimized_distance_km  = scgraph_dist_result['length']
        scgraph_distance_optimized_time_seconds = geograph_time.get_path_weight(scgraph_dist_result)
        scgraph_distance_optimized_duration     = time.time() - start_time

        # --- osmnx: shortest path by time ---
        start_time = time.time()
        origin_node      = ox.nearest_nodes(G, coord1[1], coord1[0])
        destination_node = ox.nearest_nodes(G, coord2[1], coord2[0])
        osmnx_time_path                    = ox.shortest_path(G, origin_node, destination_node, weight='travel_time')
        osmnx_time_optimized_distance_km   = route_attr_sum(G, osmnx_time_path, 'length') / 1000
        osmnx_time_optimized_time_seconds  = route_attr_sum(G, osmnx_time_path, 'travel_time')
        osmnx_time_optimized_duration      = time.time() - start_time

        # --- osmnx: shortest path by distance ---
        start_time = time.time()
        origin_node      = ox.nearest_nodes(G, coord1[1], coord1[0])
        destination_node = ox.nearest_nodes(G, coord2[1], coord2[0])
        osmnx_dist_path                        = ox.shortest_path(G, origin_node, destination_node, weight='length')
        osmnx_distance_optimized_distance_km   = route_attr_sum(G, osmnx_dist_path, 'length') / 1000
        osmnx_distance_optimized_time_seconds  = route_attr_sum(G, osmnx_dist_path, 'travel_time')
        osmnx_distance_optimized_duration      = time.time() - start_time

        # --- google: bicycle routing ---
        start_time = time.time()
        google_distance_km, google_time_seconds = get_google_dist_and_time(coord1, coord2)
        google_duration = time.time() - start_time

        data.append({
            'origin':      loc1,
            'destination': loc2,

            'scgraph_time_optimized_distance_km':       scgraph_time_optimized_distance_km,
            'scgraph_time_optimized_time_seconds':      scgraph_time_optimized_time_seconds,
            'scgraph_time_optimized_duration_seconds':  scgraph_time_optimized_duration,

            'osmnx_time_optimized_distance_km':         osmnx_time_optimized_distance_km,
            'osmnx_time_optimized_time_seconds':        osmnx_time_optimized_time_seconds,
            'osmnx_time_optimized_duration_seconds':    osmnx_time_optimized_duration,

            'scgraph_distance_optimized_distance_km':      scgraph_distance_optimized_distance_km,
            'scgraph_distance_optimized_time_seconds':     scgraph_distance_optimized_time_seconds,
            'scgraph_distance_optimized_duration_seconds': scgraph_distance_optimized_duration,

            'osmnx_distance_optimized_distance_km':        osmnx_distance_optimized_distance_km,
            'osmnx_distance_optimized_time_seconds':       osmnx_distance_optimized_time_seconds,
            'osmnx_distance_optimized_duration_seconds':   osmnx_distance_optimized_duration,

            'google_distance_km':                          google_distance_km,
            'google_time_seconds':                         google_time_seconds,
            'google_duration_seconds':                     google_duration,
        })

pamda.write_csv(filename='outputs/cambridge_osmnx_scgraph_comparison.csv', data=data)