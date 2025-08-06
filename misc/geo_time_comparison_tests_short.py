from time import time
from pamda import pamda

from utils.solvers import (
    test_google,
    test_world_highways_scgraph,
    test_us_freeway_scgraph,
    test_osmnx,
    test_haversine,
    test_haversine_circuity,
)



cities = {
    'Boston': (42.3601, -71.0589),
    'Burlington': (44.4759, -73.2121),
    'Schenectady': (42.8142, -73.9396),
    'Albany': (42.6526, -73.7562),
    'Syracuse': (43.0481, -76.1474),
    'Portland': (43.6615, -70.2553),
    'New Haven': (41.3083, -72.9279),
    'Hartford': (41.7658, -72.6734)
}

#TODO: Remove this hack to avoid hitting google every time
prev_output = pamda.read_csv('geo_time_comparison_tests_short.csv')


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
                # test_google
            ]:
                time_start = time()
                length = function(coord1, coord2)
                elapsed_time = time() - time_start
                output_item[f"{function.__name__}_time_ms"] = elapsed_time * 1000
                output_item[f"{function.__name__}_length_km"] = length


            # TODO: Remove this hack to avoid hitting google every time
            output_item['test_google_time_ms'] = prev_output[idx]['test_google_time_ms']
            output_item['test_google_length_km'] = prev_output[idx]['test_google_length_km']
            idx += 1
            # End hack


            output.append(output_item)
            # print(f"{city1} to {city2}: {output_item}")
    cities_fully_visited.append(city1)

pamda.write_csv(
    data=output,
    filename="outputs/geo_time_comparison_tests_short.csv",
)