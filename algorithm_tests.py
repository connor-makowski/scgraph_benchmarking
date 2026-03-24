import time
from pamda.pamda_timer import pamda_timer
from pamda import pamda
from scgraph import GeoGraph

# 10 US coastal cities
cities = {
    'los_angeles':   {'latitude': 34.0522, 'longitude': -118.2437},
    'san_francisco': {'latitude': 37.7749, 'longitude': -122.4194},
    'seattle':       {'latitude': 47.6062, 'longitude': -122.3321},
    'portland_or':   {'latitude': 45.5051, 'longitude': -122.6750},
    'tampa_bay':     {'latitude': 27.9506, 'longitude':  -82.4572},
    'new_york':      {'latitude': 40.7128, 'longitude':  -74.0060},
    'boston':        {'latitude': 42.3601, 'longitude':  -71.0589},
    'houston':       {'latitude': 29.7604, 'longitude':  -95.3698},
    'new_orleans':   {'latitude': 29.9511, 'longitude':  -90.0715},
    'charleston':    {'latitude': 32.7765, 'longitude':  -79.9311},
}

city_names = list(cities.keys())
city_list = [cities[c] for c in city_names]

city_pairs = [
    (city_names[i], city_names[j], cities[city_names[i]], cities[city_names[j]])
    for i in range(len(city_names))
    for j in range(len(city_names))
]

geograph_names = [
    'marnet',
    'oak_ridge_maritime',
    'north_america_rail',
    'us_freeway',
    'world_highways_and_marnet',
    'world_highways',
    'world_railways',
]


def dijkstra_solve(geograph, origin, destination):
    return geograph.get_shortest_path(
        origin_node=origin, destination_node=destination,
        output_units='km', algorithm_fn='dijkstra',
    )['length']


def a_star_solve(geograph, origin, destination):
    return geograph.get_shortest_path(
        origin_node=origin, destination_node=destination,
        output_units='km', algorithm_fn='a_star',
        algorithm_kwargs={'heuristic_fn': geograph.haversine},
    )['length']


def cached_solve(geograph, origin, destination):
    return geograph.get_shortest_path(
        origin_node=origin, destination_node=destination,
        output_units='km', algorithm_fn='cached_shortest_path',
    )['length']


def ch_solve(geograph, origin, destination):
    return geograph.get_shortest_path(
        origin_node=origin, destination_node=destination,
        output_units='km', algorithm_fn='contraction_hierarchy',
    )['length']

algorithms = [
    ('dijkstra',              dijkstra_solve),
    ('a_star',                a_star_solve),
    ('cached_shortest_path',  cached_solve),
    ('contraction_hierarchy', ch_solve),
]

output = []

for graph_name in geograph_names:
    print(f"Testing graph: {graph_name}")
    geograph = GeoGraph.load_geograph(graph_name)
    print('Building contraction hierarchy for graph (one-time timing)...')
    # CH build (one-time timing)
    t0 = time.perf_counter()
    geograph.graph_object.create_contraction_hierarchy()
    elapsed = (time.perf_counter() - t0) * 1000
    output.append({
        'function': 'create_contraction_hierarchy',
        'unit': 'ms',
        'time': elapsed,
        'avg_time_per_dist': 0,
        'graph': graph_name,
    })

    num_combinations = len(city_pairs)

    # Distance matrix (one-time timing, all 10 cities)
    print('Calculating distance matrix for graph (one-time timing)...')
    t0 = time.perf_counter()
    geograph.distance_matrix(city_list, output_units='km')
    elapsed = (time.perf_counter() - t0) * 1000
    output.append({
        'function': 'distance_matrix_first_pass',
        'unit': 'ms',
        'time': elapsed,
        'avg_time_per_dist': elapsed / num_combinations,
        'graph': graph_name,
    })

    t0 = time.perf_counter()
    geograph.distance_matrix(city_list, output_units='km')
    elapsed = (time.perf_counter() - t0) * 1000
    output.append({
        'function': 'distance_matrix_second_pass',
        'unit': 'ms',
        'time': elapsed,
        'avg_time_per_dist': elapsed / num_combinations,
        'graph': graph_name,
    })

    geograph.graph_object.reset_cache()

    print('Calculating shortest paths...')
    for algo_name, solver_fn in algorithms:
        print(f"    Testing algorithm: {algo_name}")
        output_data = {
            'first_pass': [],
            'second_pass': [],
        }

        for pass_type in ['first_pass', 'second_pass']:
            for origin_name, dest_name, origin, destination in city_pairs:
                # First pass (one-time timing)
                t0 = time.perf_counter()
                dist = solver_fn(geograph, origin, destination)
                elapsed = (time.perf_counter() - t0) * 1000
                output_data[pass_type].append(elapsed)

        

        first_pass_info = {
            'function': f"distance_matrix_{algo_name}_first_pass",
            'unit': 'ms',
            'time': sum(output_data['first_pass']),
            'avg_time_per_dist': sum(output_data['first_pass']) / num_combinations,
            'graph': graph_name
        }
        output.append(first_pass_info)

        second_pass_info = {
            'function': f"distance_matrix_{algo_name}_second_pass",
            'unit': 'ms',
            'time': sum(output_data['second_pass']),
            'avg_time_per_dist': sum(output_data['second_pass']) / num_combinations,
            'graph': graph_name
        }
        output.append(second_pass_info)


pamda.write_csv(data=output, filename='outputs/algorithm_tests.csv')
