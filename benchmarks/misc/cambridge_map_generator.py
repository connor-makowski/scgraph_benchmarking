import os
import matplotlib.pyplot as plt
import osmnx as ox
import polyline
import requests
from pamda import pamda
from scgraph import GeoGraph

keys = pamda.read_json('keys.json')
google_api_key = keys.get('google_api_key')


def get_google_route(coord1, coord2):
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": google_api_key,
        "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline",
    }
    body = {
        "origin": {"location": {"latLng": {"latitude": coord1[0], "longitude": coord1[1]}}},
        "destination": {"location": {"latLng": {"latitude": coord2[0], "longitude": coord2[1]}}},
        "travelMode": "BICYCLE",
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code != 200:
        print(f"  Google error {response.status_code}: {response.text}")
        return None
    data = response.json()
    route = data["routes"][0]
    encoded = route["polyline"]["encodedPolyline"]
    return polyline.decode(encoded)


G = ox.graph_from_place(
    ['Somerville, Massachusetts, USA', 'Cambridge, Massachusetts, USA'],
    network_type='bike',
)
G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)

geograph_time     = GeoGraph.load_from_osmnx_graph(G, weight_key='travel_time')
geograph_distance = GeoGraph.load_from_osmnx_graph(G, weight_key='length')

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

os.makedirs('outputs/cambridge', exist_ok=True)

for loc1, coord1 in locations.items():
    for loc2, coord2 in locations.items():
        if loc1 == loc2:
            continue

        print(f"{loc1} -> {loc2}")

        origin      = {'latitude': coord1[0], 'longitude': coord1[1]}
        destination = {'latitude': coord2[0], 'longitude': coord2[1]}

        time_result     = geograph_time.get_shortest_path(origin_node=origin, destination_node=destination, output_path=True)
        distance_result = geograph_distance.get_shortest_path(origin_node=origin, destination_node=destination, output_path=True)
        google_coords   = get_google_route(coord1, coord2)

        fig, ax = ox.plot_graph(
            G,
            bgcolor='white',
            node_size=0,
            edge_color='#cccccc',
            edge_linewidth=0.5,
            show=False,
            close=False,
        )

        def plot_coord_path(coords, color, linewidth, alpha=0.9):
            lons = [c[1] for c in coords]
            lats = [c[0] for c in coords]
            ax.plot(lons, lats, color=color, linewidth=linewidth, alpha=alpha, solid_capstyle='round')

        plot_coord_path(time_result['coordinate_path'],     color='blue',  linewidth=3)
        plot_coord_path(distance_result['coordinate_path'], color='green', linewidth=3)
        if google_coords:
            plot_coord_path(google_coords, color='red', linewidth=2)

        ax.plot([], [], color='blue',  linewidth=3, label='scgraph / osmnx (time)')
        ax.plot([], [], color='green', linewidth=3, label='scgraph / osmnx (distance)')
        ax.plot([], [], color='red',   linewidth=2, label='Google')
        ax.legend(loc='best', fontsize=8)
        ax.set_title(f"{loc1} → {loc2}", fontsize=10)

        slug1 = loc1.lower().replace(' ', '_')
        slug2 = loc2.lower().replace(' ', '_')
        fig.savefig(f"outputs/cambridge/{slug1}_to_{slug2}.png", dpi=150, bbox_inches='tight')
        plt.close(fig)

print("Done.")
