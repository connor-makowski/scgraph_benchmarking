import time
from pamda.pamda_timer import pamda_timer
from pamda import pamda

from utils.solvers import (
    test_google,
    test_world_highways_scgraph,
    test_us_freeway_scgraph,
    build_osmnx_graph,
    solve_nx_on_osmnx,
    solve_scgraph_on_osmnx,
)
from utils.graphs import make_scgraph_from_osmnx

# Los Angeles to San Diego
LA = (34.0522, -118.2437)
SD = (32.7157, -117.1611)

# Orlando to Tampa
ORL = (28.5383, -81.3792)
TAM = (27.9506, -82.4572)

# New York City to Philadelphia
NYC = (40.7128, -74.0060)
PHI = (39.9526, -75.1652)

combinations = [("LA_SD", LA, SD), ("ORL_TAM", ORL, TAM), ("NYC_PHI", NYC, PHI)]

nx_solve_timer = pamda_timer(solve_nx_on_osmnx, iterations=10)
scgraph_solve_timer = pamda_timer(solve_scgraph_on_osmnx, iterations=10)
wh = pamda_timer(test_world_highways_scgraph, iterations=10)
uf = pamda_timer(test_us_freeway_scgraph, iterations=10)
go = pamda_timer(test_google, iterations=10)

output = []

for combo_name, coord1, coord2 in combinations:

    # Data prep: OSMNx graph build (one-time timing)
    t0 = time.perf_counter()
    G = build_osmnx_graph(coord1, coord2)
    elapsed = (time.perf_counter() - t0) * 1000  # convert to milliseconds
    output.append({
        'module': 'data_prep',
        'function': 'build_osmnx_graph',
        'unit': 'ms',
        'iterations': 1,
        'avg': elapsed,
        'min': elapsed,
        'max': elapsed,
        'std': 0,
        'combination': combo_name,
        'category': 'data_prep',
        'solver': 'osmnx_build',
        'distance_km': None,

    })

    # Data prep: SCGraph conversion from OSMNx (one-time timing)
    t0 = time.perf_counter()
    geograph = make_scgraph_from_osmnx(G)
    elapsed = (time.perf_counter() - t0) * 1000  # convert to milliseconds
    output.append({
        'module': 'data_prep',
        'function': 'make_scgraph_from_osmnx',
        'unit': 'ms',
        'iterations': 1,
        'avg': elapsed,
        'min': elapsed,
        'max': elapsed,
        'std': 0,
        'combination': combo_name,
        'category': 'data_prep',
        'solver': 'scgraph_from_osmnx_convert',
        "distance_km": None,
    })

    # Network solve: OSMNx + NetworkX
    item = nx_solve_timer.get_time_stats(G, coord1, coord2)
    item['combination'] = combo_name
    item['category'] = 'network_solve'
    item['solver'] = 'osmnx_nx'
    item['distance_km'] = solve_nx_on_osmnx(G, coord1, coord2)
    output.append(item)

    # Network solve: OSMNx + SCGraph
    item = scgraph_solve_timer.get_time_stats(geograph, coord1, coord2)
    item['combination'] = combo_name
    item['category'] = 'network_solve'
    item['solver'] = 'osmnx_scgraph'
    item['distance_km'] = solve_scgraph_on_osmnx(geograph, coord1, coord2)
    output.append(item)

    # Network solve: World Highways SCGraph
    item = wh.get_time_stats(coord1, coord2)
    item['combination'] = combo_name
    item['category'] = 'network_solve'
    item['solver'] = 'world_highways_scgraph'
    item['distance_km'] = wh(coord1, coord2)
    output.append(item)

    # Network solve: US Freeway SCGraph
    item = uf.get_time_stats(coord1, coord2)
    item['combination'] = combo_name
    item['category'] = 'network_solve'
    item['solver'] = 'us_freeway_scgraph'
    item['distance_km'] = uf(coord1, coord2)
    output.append(item)

    # Network solve: Google
    item = go.get_time_stats(coord1, coord2)
    item['combination'] = combo_name
    item['category'] = 'network_solve'
    item['solver'] = 'google'
    item['distance_km'] = go(coord1, coord2)
    output.append(item)

pamda.write_csv(data=output, filename='outputs/time_dist_comparisons.csv')
