import requests
from pamda import pamda
from scgraph.utils import haversine
from scgraph import GeoGraph

world_highways_geograph = GeoGraph.load_geograph('world_highways')
us_freeway_geograph = GeoGraph.load_geograph('us_freeway')

import osmnx as ox
import networkx as nx

keys = pamda.read_json('utils/keys.json')
google_api_key = keys.get('google_api_key') 


##############################################
# Functions for timing distance calculations #
##############################################

def test_google(coord1, coord2, mode="driving"):
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": google_api_key,
        "X-Goog-FieldMask": "routes.duration,routes.distanceMeters"
    }

    body = {
        "origin": {
            "location": {
                "latLng": {
                    "latitude": coord1[0],
                    "longitude": coord1[1]
                }
            }
        },
        "destination": {
            "location": {
                "latLng": {
                    "latitude": coord2[0],
                    "longitude": coord2[1]
                }
            }
        },
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_UNAWARE"
    }

    response = requests.post(url, headers=headers, json=body)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None

    data = response.json()
    distance_meters = data["routes"][0]["distanceMeters"]
    return distance_meters / 1000  # in km

def test_world_highways_scgraph(coord1, coord2):
    output = world_highways_geograph.get_shortest_path(
        origin_node={"latitude": coord1[0], "longitude": coord1[1]},
        destination_node={"latitude": coord2[0], "longitude": coord2[1]},
        output_units="km",
        off_graph_circuity=1.2
    )
    # print(f"Scgraph distance: {output['length']:.2f} km")
    return output['length']

def test_us_freeway_scgraph(coord1, coord2):
    output = us_freeway_geograph.get_shortest_path(
        origin_node={"latitude": coord1[0], "longitude": coord1[1]},
        destination_node={"latitude": coord2[0], "longitude": coord2[1]},
        output_units="km",
        off_graph_circuity=1.2
    )
    # print(f"Scgraph distance: {output['length']:.2f} km")
    return output['length']

def test_haversine(coord1, coord2):
    return haversine(coord1, coord2, units="km")

def test_haversine_circuity(coord1, coord2):
    return haversine(coord1, coord2, units="km", circuity=1.2)




# OSMNx
ox.settings.log_console = False
ox.settings.use_cache = True

def build_graph_between_coords(coord1, coord2, buffer_km=50):
    # Create a bounding box that covers both points with a buffer
    mid_lat = (coord1[0] + coord2[0]) / 2
    mid_lon = (coord1[1] + coord2[1]) / 2

    max_dist = haversine(coord1, coord2, units='m')
    buffer_dist = max_dist / 2 + buffer_km * 1000  # in meters

    # Filter for major roads only
    custom_filter = ('["highway"]["area"!~"yes"]'
                     '["highway"~"motorway|trunk|primary"]')

    G = ox.graph_from_point((mid_lat, mid_lon), dist=buffer_dist,
                            network_type='drive', custom_filter=custom_filter)
    return G


##############################################
# Functions for timing distance calculations #
##############################################

def test_osmnx(coord1, coord2):
    print(f"\nComputing route from {coord1} to {coord2}...")

    # Build the graph
    G = build_graph_between_coords(coord1, coord2)

    # Find nearest nodes
    orig_node = ox.distance.nearest_nodes(G, X=coord1[1], Y=coord1[0])
    dest_node = ox.distance.nearest_nodes(G, X=coord2[1], Y=coord2[0])

    try:
        # Compute shortest path length (in meters)
        length_m = nx.shortest_path_length(G, orig_node, dest_node, weight='length')  # Convert to kilometers
        length_km = length_m / 1000  # Convert to kilometers
        # print(f"OSMNx distance: {length_km:.2f} km")
        return length_km
    except nx.NetworkXNoPath:
        # print("No path found between these coordinates on the filtered road network.")
        return None