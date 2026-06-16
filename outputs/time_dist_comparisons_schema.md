# time_dist_comparisons.csv — Field Reference

Compares data-prep and solve timing across solvers for 3 city pairs (LA→SD, ORL→TAM, NYC→PHI). Rows use a long/tidy format — each row is one (function, city-pair) timing result. Network solve rows use 10 iterations via `pamda_timer`; data-prep rows use 1 iteration.

---

## Fields

| Field | Description |
|---|---|
| `module` | Python module where the timed function lives (e.g. `utils.solvers`, `data_prep`) |
| `function` | Name of the function that was timed |
| `unit` | Time unit — always `ms` |
| `iterations` | Number of timing iterations (`1` for data_prep, `10` for network_solve) |
| `avg` | Average time (ms) across iterations |
| `min` | Minimum time (ms) across iterations |
| `max` | Maximum time (ms) across iterations |
| `std` | Standard deviation (ms) across iterations |
| `combination` | City-pair abbreviation (`LA_SD`, `ORL_TAM`, `NYC_PHI`) |
| `category` | Row type: `data_prep` (one-time setup cost) or `network_solve` (per-query solve) |
| `solver` | Solver identifier (see table below) |
| `distance_km` | Route distance (km); blank for `data_prep` rows |

---

## `category` values

| `category` | Description |
|---|---|
| `data_prep` | One-time cost to download and build the graph for a city pair — not repeated per query |
| `network_solve` | Per-query solve cost, averaged over 10 iterations |

---

## `solver` values

| `solver` | Description |
|---|---|
| `osmnx_build` | OSMNx graph download + construction (`build_osmnx_graph`) |
| `scgraph_from_osmnx_convert` | Conversion of an OSMNx graph to a scgraph GeoGraph |
| `osmnx_nx` | NetworkX Dijkstra on the pre-built OSMNx graph |
| `osmnx_scgraph` | scgraph `get_shortest_path` on the OSMNx-derived GeoGraph |
| `world_highways_scgraph` | scgraph on the built-in `world_highways` geograph |
| `us_freeway_scgraph` | scgraph on the built-in `us_freeway` geograph |
| `google` | Google Routes API v2 (driving, traffic-unaware) |

---

## Notes

- `data_prep` rows have `iterations=1` and `std=0` since they are not repeated.
- `osmnx_build` is the dominant data-prep cost — it downloads OSM data from the internet for the region around each city pair.
- Built-in scgraph geographs (`world_highways`, `us_freeway`) have no data-prep row because they are loaded once at module import and reused across all calls.
- Google has no data-prep row; its `network_solve` timing includes full API round-trip latency.
