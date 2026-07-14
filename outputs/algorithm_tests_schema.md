# algorithm_tests.csv — Field Reference

Benchmarks every scgraph algorithm on 7 built-in geographs against 10 US coastal cities (100 city-pairs each). Each row is one function/graph combination.

---

## Fields

| Field | Description |
|---|---|
| `function` | Name of the operation being timed (see categories below) |
| `unit` | Time unit — always `ms` |
| `time` | Total elapsed time (ms) for the operation |
| `avg_time_per_dist` | Average time per origin-destination pair (ms); `0` for one-time build operations that are not per-pair |
| `graph` | Built-in geograph the test was run on |

---

## `function` values

### One-time build operations
These run once per graph before any routing. `avg_time_per_dist` is `0`.

| `function` | Description |
|---|---|
| `create_contraction_hierarchy` | Time to build the Contraction Hierarchy index |
| `create_tnr_hierarchy` | Time to build the Transit Node Routing index |

### Distance matrix passes
Each pass solves all 100 city-pairs. Pass 2 benefits from cached shortest-path trees left over from pass 1.

| `function` | Description |
|---|---|
| `dijkstra_distance_matrix_pass_1` | All 100 pairs solved via Dijkstra (first pass) |
| `dijkstra_distance_matrix_pass_2` | All 100 pairs solved via Dijkstra (second pass, cached trees) |
| `a_star_distance_matrix_pass_1` | All 100 pairs via A\* (first pass) |
| `a_star_distance_matrix_pass_2` | All 100 pairs via A\* (second pass) |
| `cached_shortest_path_distance_matrix_pass_1` | All 100 pairs via cached shortest path (first pass) |
| `cached_shortest_path_distance_matrix_pass_2` | All 100 pairs via cached shortest path (second pass) |
| `contraction_hierarchy_distance_matrix_pass_1` | All 100 pairs via CH (first pass) |
| `contraction_hierarchy_distance_matrix_pass_2` | All 100 pairs via CH (second pass) |
| `tnr_distance_matrix_pass_1` | All 100 pairs via TNR (first pass) |
| `tnr_distance_matrix_pass_2` | All 100 pairs via TNR (second pass) |
| `dijkstra_buckets_distance_matrix_pass_1` | All 100 pairs via Dijkstra Buckets (first pass) |
| `dijkstra_buckets_distance_matrix_pass_2` | All 100 pairs via Dijkstra Buckets (second pass) |
| `distance_matrix_bellman_ford_first_pass` | All 100 pairs via Bellman-Ford (single pass — no caching, so no second pass) |

---

## `graph` values

`marnet`, `oak_ridge_maritime`, `north_america_rail`, `us_freeway`, `world_highways_and_marnet`, `world_highways`, `world_railways`
