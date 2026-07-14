# path_algorithm_time_tests.csv — Field Reference

Head-to-head timing of scgraph vs NetworkX vs igraph across GeoGraph and GridGraph test cases. Each row is one (graph, test case) combination. All solve times are averages over 10 iterations via `pamda_timer`.

---

## Graph / Case Identifiers

| Field | Description |
|---|---|
| `graph_name` | Name of the graph under test (e.g. `World Highways`, `GridGraph 100x100`) |
| `case_name` | Test case label within the graph (`case_1` through `case_4`) |
| `graph_nodes` | Number of nodes in the graph |
| `graph_edges` | Number of edges in the graph |
| `node_steps_needed` | Number of node hops in the optimal path for this case |

---

## One-time Build Times

Measured once per graph (not per case). Blank for graph types where the algorithm is not applicable.

| Field | Description |
|---|---|
| `sc_ch_build_ms` | Time (ms) to build scgraph's Contraction Hierarchy index |
| `sc_tnr_build_ms` | Time (ms) to build scgraph's Transit Node Routing index |

---

## Solver Times (avg of 10 iterations)

| Field | Description |
|---|---|
| `nx_dijkstra_time_ms` | NetworkX `dijkstra_predecessor_and_distance` average solve time (ms) |
| `ig_shortest_path_time_ms` | igraph `get_shortest_paths` average solve time (ms) |
| `sc_dijkstra_modified_time_ms` | scgraph modified Dijkstra average solve time (ms) |
| `sc_a_star_time_ms` | scgraph A\* average solve time (ms) |
| `sc_dijkstra_buckets_time_ms` | scgraph Dijkstra Buckets average solve time (ms) |
| `sc_bmssp_time_ms` | scgraph BMSSP average solve time (ms) |
| `sc_bellman_ford_time_ms` | scgraph Bellman-Ford average solve time (ms) |
| `sc_ch_time_ms` | scgraph Contraction Hierarchy average solve time (ms) |
| `sc_tnr_time_ms` | scgraph Transit Node Routing average solve time (ms) |

---

## Standard Deviations (across 10 iterations)

One `_stdev` column per solver, in the same order as the time columns above.

| Field | Description |
|---|---|
| `nx_dijkstra_stdev` | Std dev (ms) of NetworkX Dijkstra times |
| `ig_shortest_path_stdev` | Std dev (ms) of igraph times |
| `sc_dijkstra_modified_stdev` | Std dev (ms) of scgraph modified Dijkstra times |
| `sc_a_star_stdev` | Std dev (ms) of scgraph A\* times |
| `sc_dijkstra_buckets_stdev` | Std dev (ms) of scgraph Dijkstra Buckets times |
| `sc_bmssp_stdev` | Std dev (ms) of scgraph BMSSP times |
| `sc_bellman_ford_stdev` | Std dev (ms) of scgraph Bellman-Ford times |
| `sc_ch_stdev` | Std dev (ms) of scgraph CH times |
| `sc_tnr_stdev` | Std dev (ms) of scgraph TNR times |

---

## Notes

- CH and TNR are only benchmarked on GeoGraph types, not GridGraphs — those cells are blank.
- BMSSP is a bidirectional multi-source shortest path variant and tends to be slower on sparse graphs.
- Bellman-Ford is only run on graphs with fewer than 50,000 nodes (`sc_bellman_ford_time_ms`/`sc_bellman_ford_stdev` are blank above that threshold), since it is dramatically slower than the other solvers on large graphs (seconds per solve vs. ms).
- GridGraphs include a center-column wall (blocking rows 5+) to create non-trivial routing scenarios.
- `node_steps_needed` is the path length in hops for the specific test case — useful for normalizing timing across cases of different difficulty.
