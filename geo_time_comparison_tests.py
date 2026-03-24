from time import time
from pamda import pamda

from utils.solvers import (
    test_google,
    test_world_highways_scgraph,
    test_us_freeway_scgraph,
    test_haversine,
    test_haversine_circuity,
)


cities = {
    'Los Angeles': (34.0522, -118.2437),
    'New York City': (40.7128, -74.0060),
    'Chicago': (41.8781, -87.6298),
    'Houston': (29.7604, -95.3698),
    'Phoenix': (33.4484, -112.0740),
    'Denver': (39.7392, -104.9903),
    'Seattle': (47.6062, -122.3321),
    'Miami': (25.7617, -80.1918),
    'Washington D.C.': (38.9072, -77.0369),
    'San Francisco': (37.7749, -122.4194),
    'Omaha': (41.2565, -95.9345),
    'Atlanta': (33.7490, -84.3880),
    'Austin': (30.2672, -97.7431),
    'Boston': (42.3601, -71.0589),
    'Las Vegas': (36.1699, -115.1398),
    'Detroit': (42.3314, -83.0458)
}

# Uncomment this hack to avoid hitting google every time
prev_output = pamda.read_csv('outputs/geo_time_comparison_tests.csv')


output = []
idx = 0
# For each pair of cities, calculate distances using all three methods
cities_fully_visited = []
print("\nDistance Calculations Between Cities:")
for city1, coord1 in cities.items():
    print(f"Calculating distances from {city1}...")
    for city2, coord2 in cities.items():
        if city1 != city2 and city2 not in cities_fully_visited:
            output_item = {
                'city1': city1,
                'city2': city2,
                'coord1': coord1,
                'coord2': coord2
            }
            for function in [
                test_world_highways_scgraph,
                test_us_freeway_scgraph,
                test_haversine,
                test_haversine_circuity,
                # test_google,
            ]:
                time_start = time()
                length = function(coord1, coord2)
                elapsed_time = time() - time_start
                output_item[f"{function.__name__}_time_ms"] = elapsed_time * 1000
                output_item[f"{function.__name__}_length_km"] = length


            # Uncomment this hack to avoid hitting google every time (comment out test_google above)
            output_item['test_google_time_ms'] = prev_output[idx]['test_google_time_ms']
            output_item['test_google_length_km'] = prev_output[idx]['test_google_length_km']
            idx += 1
            # End hack


            output.append(output_item)
            # print(f"{city1} to {city2}: {output_item}")
    cities_fully_visited.append(city1)

pamda.write_csv(
    data=output,
    filename="outputs/geo_time_comparison_tests.csv",
)