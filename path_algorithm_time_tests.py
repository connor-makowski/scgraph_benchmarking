from scgraph import Graph as SCGraph
from scgraph import GeoGraph 

world_highways_and_marnet_geograph = GeoGraph.load_geograph('world_highways_and_marnet')
world_highways_geograph = GeoGraph.load_geograph('world_highways')
us_freeway_geograph = GeoGraph.load_geograph('us_freeway')

# Other utilities
from pamda import pamda
from pamda.pamda_timer import pamda_timer

from utils.graphs import make_nxgraph, igraph_from_scgraph, make_gridgraph, get_nx_shortest_path, get_igraph_shortest_path


graph_data = [
    ('World Highways', world_highways_geograph),
    ('World Highways and Marnet', world_highways_and_marnet_geograph),
    ('US Freeway', us_freeway_geograph),
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
    scgraph_graph = scgraph_object.graph
    scgraph_graph_object = scgraph_object.graph_object

    nxgraph = make_nxgraph(scgraph_graph)
    igraph = igraph_from_scgraph(scgraph_graph)
    
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

    # print("Preprocessing contraction hierarchy...")
    # scgraph_object.create_contraction_hierarchy()
    # print("Done")

    graph_nodes = len(scgraph_graph)
    graph_edges = nxgraph.number_of_edges()


    for case_name, origin, destination in test_cases:
        print(f"\nTesting {case_name}...")

        solved = scgraph_graph_object.dijkstra(origin_id=origin, destination_id=destination)
        # print(f"Total nodes: {len(scgraph)} | Total edges: {nxgraph.number_of_edges()} | Steps Needed: {len(solved['path'])}")

        nx_dijkstra_time_stats = pamda_timer(get_nx_shortest_path, iterations = 10).get_time_stats(graph=nxgraph, origin=origin, destination=destination)
        print(f"NetworkX Dijkstra time: {nx_dijkstra_time_stats['avg']:.2f} ms (stdev: {nx_dijkstra_time_stats['std']:.2f})")

        ig_shortest_path_time_stats = pamda_timer(get_igraph_shortest_path, iterations = 10).get_time_stats(graph=igraph, origin=origin, destination=destination)
        print(f"iGraph Shortest Path time: {ig_shortest_path_time_stats['avg']:.2f} ms (stdev: {ig_shortest_path_time_stats['std']:.2f})")

        sc_dijkstra_modified_time_stats = pamda_timer(scgraph_graph_object.dijkstra, iterations = 10).get_time_stats(origin_id=origin, destination_id=destination)
        print(f"SCGraph Dijkstra time: {sc_dijkstra_modified_time_stats['avg']:.2f} ms (stdev: {sc_dijkstra_modified_time_stats['std']:.2f})")

        sc_a_star_time_stats = pamda_timer(scgraph_graph_object.a_star, iterations = 10).get_time_stats(origin_id=origin, destination_id=destination, heuristic_fn=a_star_heuristic)
        print(f"SCGraph A* time: {sc_a_star_time_stats['avg']:.2f} ms (stdev: {sc_a_star_time_stats['std']:.2f})")

        # sc_ch_time_stats = pamda_timer(scgraph_graph_object.contraction_hierarchy, iterations = 10).get_time_stats(origin_id=origin, destination_id=destination)
        # print(f"SCGraph CH time: {sc_ch_time_stats['avg']:.2f} ms (stdev: {sc_ch_time_stats['std']:.2f})")

        sc_bmssp_time_stats = pamda_timer(scgraph_graph_object.bmssp, iterations = 10).get_time_stats(origin_id=origin, destination_id=destination)
        print(f"SCGraph BMSSP time: {sc_bmssp_time_stats['avg']:.2f} ms (stdev: {sc_bmssp_time_stats['std']:.2f})")

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
            # 'sc_ch_time_ms': sc_ch_time_stats['avg'],
            'sc_bmssp_time_ms': sc_bmssp_time_stats['avg'],
            'nx_dijkstra_stdev': nx_dijkstra_time_stats['std'],
            'ig_shortest_path_stdev': ig_shortest_path_time_stats['std'],
            'sc_dijkstra_modified_stdev': sc_dijkstra_modified_time_stats['std'],
            'sc_a_star_stdev': sc_a_star_time_stats['std'],
            # 'sc_ch_stdev': sc_ch_time_stats['std'],
            'sc_bmssp_stdev': sc_bmssp_time_stats['std']
        })

pamda.write_csv(
    filename="outputs/path_algorithm_time_tests.csv",
    data=output
)