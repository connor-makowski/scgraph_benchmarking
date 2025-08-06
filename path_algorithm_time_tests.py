from scgraph_data.world_highways_and_marnet import world_highways_and_marnet_geograph
from scgraph_data.world_highways import world_highways_geograph
from scgraph.geographs.us_freeway import us_freeway_geograph
from scgraph.core import Graph as SCGraph

# Other utilities
from pamda import pamda
from pamda.pamda_timer import pamda_timer

from utils.graphs import make_nxgraph, make_igraph, make_gridgraph, get_nx_shortest_path, get_igraph_shortest_path


graph_data = [
    # ('World Highways', world_highways_geograph),
    # ('World Highways and Marnet', world_highways_and_marnet_geograph),
    # ('US Freeway', us_freeway_geograph),
    ('100x100 GridGraph', make_gridgraph(100, 100)),
    ('100x200 GridGraph', make_gridgraph(100, 200)),
    ('100x400 GridGraph', make_gridgraph(100, 400)),
    ('100x800 GridGraph', make_gridgraph(100, 800)),
    ('100x1600 GridGraph', make_gridgraph(100, 1600)),
    ('100x3200 GridGraph', make_gridgraph(100, 3200)),
    ('100x6400 GridGraph', make_gridgraph(100, 6400)),
    ('300x300 GridGraph', make_gridgraph(300, 300)),

]

output = []

print("\n===============\nIGraph vs NetworkX vs SCGraph Time Tests:\n===============")
for name, scgraph_object in graph_data:
    print(f"\n{name}:")
    scgraph = scgraph_object.graph
    nxgraph = make_nxgraph(scgraph)
    igraph = make_igraph(scgraph)

    if 'gridgraph' in name.lower():
        a_star_heuristic = scgraph_object.euclidean_heuristic
        test_cases = [
            ('bottomLeft_wall_topRight', scgraph_object.get_idx(**{"x": 5, "y": 5}), scgraph_object.get_idx(**{"x": scgraph_object.x_size-5, "y": scgraph_object.y_size-5})),
            ('topLeft_wall_topRight', scgraph_object.get_idx(**{"x": 5, "y": scgraph_object.y_size-5}), scgraph_object.get_idx(**{"x": scgraph_object.x_size-5, "y": scgraph_object.y_size-5})),
            ('up_5_over_5',scgraph_object.get_idx(**{"x": 5, "y": 5}), scgraph_object.get_idx(**{"x": 10, "y": 10})),
            ('bottomLeft_bottomRight',scgraph_object.get_idx(**{"x": 5, "y": 5}), scgraph_object.get_idx(**{"x": scgraph_object.x_size-5, "y": 5})),
        ]
    else:
        a_star_heuristic = scgraph_object.haversine
        test_cases = [
            ('case_1', 0, 4000),
            ('case_2', 100, 2000),
            ('case_3', 1000, 200),
            ('case_4', 5000, 1500)
        ]

    graph_nodes = len(scgraph)
    graph_edges = nxgraph.number_of_edges()


    for case_name, origin, destination in test_cases:
        print(f"\nTesting {case_name}...")
        solved = SCGraph.a_star(graph=scgraph, origin_id=origin, destination_id=destination, heuristic_fn=a_star_heuristic)
        # print(f"Total nodes: {len(scgraph)} | Total edges: {nxgraph.number_of_edges()} | Steps Needed: {len(solved['path'])}")

        nx_dijkstra_time_stats = pamda_timer(get_nx_shortest_path, iterations = 10).get_time_stats(graph=nxgraph, origin=origin, destination=destination)
        print(f"NetworkX Dijkstra time: {nx_dijkstra_time_stats['avg']:.2f} ms (stdev: {nx_dijkstra_time_stats['std']:.2f})")

        ig_shortest_path_time_stats = pamda_timer(get_igraph_shortest_path, iterations = 10).get_time_stats(graph=igraph, origin=origin, destination=destination)
        print(f"iGraph Shortest Path time: {ig_shortest_path_time_stats['avg']:.2f} ms (stdev: {ig_shortest_path_time_stats['std']:.2f})")

        sc_dijkstra_modified_time_stats = pamda_timer(SCGraph.dijkstra_makowski, iterations = 10).get_time_stats(graph=scgraph, origin_id=origin, destination_id=destination)
        print(f"SCGraph Dijkstra-Modified time: {sc_dijkstra_modified_time_stats['avg']:.2f} ms (stdev: {sc_dijkstra_modified_time_stats['std']:.2f})")

        sc_a_star_time_stats = pamda_timer(SCGraph.a_star, iterations = 10).get_time_stats(graph=scgraph, origin_id=origin, destination_id=destination, heuristic_fn=a_star_heuristic)
        print(f"SCGraph A* time: {sc_a_star_time_stats['avg']:.2f} ms (stdev: {sc_a_star_time_stats['std']:.2f})")

        sc_dijkstra_negative_time_stats = pamda_timer(SCGraph.dijkstra_negative, iterations = 10).get_time_stats(graph=scgraph, origin_id=origin, destination_id=destination)
        print(f"SCGraph Dijkstra Negative time: {sc_dijkstra_negative_time_stats['avg']:.2f} ms (stdev: {sc_dijkstra_negative_time_stats['std']:.2f})")

        output.append({
            'graph_name': name,
            'case_name': case_name,
            'graph_nodes': graph_nodes,
            'graph_edges': graph_edges,
            'node_steps_needed': len(solved['path']),
            'nx_dijkstra_time_ms': nx_dijkstra_time_stats['avg'],
            'ig_shortest_path_time_ms': ig_shortest_path_time_stats['avg'],
            'sc_dijkstra_modified_time_ms': sc_dijkstra_modified_time_stats['avg'],
            'sc_a_star_time_ms': sc_a_star_time_stats['avg'],
            'sc_dijkstra_negative_time_ms': sc_dijkstra_negative_time_stats['avg'],
            'nx_dijkstra_stdev': nx_dijkstra_time_stats['std'],
            'ig_shortest_path_stdev': ig_shortest_path_time_stats['std'],
            'sc_dijkstra_modified_stdev': sc_dijkstra_modified_time_stats['std'],
            'sc_a_star_stdev': sc_a_star_time_stats['std'],
            'sc_dijkstra_negative_stdev': sc_dijkstra_negative_time_stats['std'],
        })

pamda.write_csv(
    filename="outputs/path_algorithm_time_tests.csv",
    data=output
)