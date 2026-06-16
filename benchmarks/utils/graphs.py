
from scgraph.grid import GridGraph
from scgraph import GeoGraph
from networkx import Graph as NXGraph, dijkstra_predecessor_and_distance
from igraph import Graph as IGGraph

def make_nxgraph(graph):
    """
    Convert a scgraph graph object to a NetworkX graph.
    """
    nxGraph = NXGraph()
    for idx_from, connections in enumerate(graph):
        for idx_to, weight in connections.items():
            nxGraph.add_edge(idx_from, idx_to, weight=weight)
    return nxGraph

def igraph_from_scgraph(graph):
    """
    Convert a scgraph graph object to an igraph graph.
    """
    edges = []
    weights = []

    for from_node, neighbors in enumerate(graph):
        for to_node, weight in neighbors.items():
            # iGraph assumes undirected graph by default, avoid adding reverse edge
            if from_node < to_node:
                edges.append((from_node, to_node))
                weights.append(weight)

    ig_graph = IGGraph(edges=edges, directed=False)
    ig_graph.es['weight'] = weights
    return ig_graph

def igraph_from_osmnx(osmnx_graph):
    """
    Convert an OSMNx graph to an igraph graph.
    """
    edges = []
    weights = []

    for u, v, data in osmnx_graph.edges(data=True):
        weight = data.get('length', 1)  # Default to 1 if no length attribute
        edges.append((u, v))
        weights.append(weight)

    ig_graph = IGGraph(edges=edges, directed=False)
    ig_graph.es['weight'] = weights
    return ig_graph


def make_gridgraph(x_size, y_size):
    # Create a wall down the middle of the grid
    blocks = [(int(x_size/2), i) for i in range(5, y_size)]
    shape = [(0, 0), (0, 1), (1, 0), (1, 1)]
    return GridGraph(
        x_size=x_size,
        y_size=y_size,
        blocks=blocks,
        shape=shape,
        add_exterior_walls=False,
)

def get_igraph_shortest_path(graph, origin, destination):
    """
    Get the shortest path in an igraph graph.
    """
    path = graph.get_shortest_paths(origin, to=destination, weights='weight', output='vpath')[0]
    length = sum(graph.es[graph.get_eid(path[i], path[i+1])]['weight'] for i in range(len(path) - 1))
    return {
        'path': path,
        'length': length
    }

def get_nx_shortest_path(graph, origin, destination):
    return dijkstra_predecessor_and_distance(G=graph, source=origin, weight='weight')

def make_scgraph_from_osmnx(osmnx_graph):
    """
    Convert an OSMNx graph to a SCGraph GeoGraph using load_from_osmnx_graph.
    """
    return GeoGraph.load_from_osmnx_graph(osmnx_graph)