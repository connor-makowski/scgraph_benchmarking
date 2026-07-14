# scgraph_benchmarking: Development Guide

## Project Purpose

This is a benchmarking and analysis repo for the [`scgraph`](https://github.com/connor-makowski/scgraph) library. It is **not** a library itself — it is a collection of standalone scripts used to:

- Benchmark `scgraph` algorithms (Dijkstra, A\*, BMSSP, Dijkstra Buckets, CH, TNR, cached) across built-in geographs
- Compare `scgraph` performance against `NetworkX` and `igraph`
- Compare routing accuracy and timing against Google Routes API
- Compare `scgraph` solving on OSMNx graphs vs. NetworkX on the same OSMNx graphs
- Benchmark OSRM (Docker-based) for setup/preprocessing time and per-query performance
- Compare `scgraph` and OSMNx routing on a local Cambridge/Somerville bike network

Results are written to CSV files in `outputs/` and analyzed in a Jupyter notebook.

---

## Directory Layout

```
benchmarks/                             # Benchmark scripts and related files
  algorithm_tests.py                    # Benchmark all scgraph algorithms per geograph (first + second pass)
  cambridge_osmnx_scgraph_comparison.py # Compare scgraph vs OSMNx vs Google on Cambridge bike network
  geo_time_comparison_tests.py          # Compare scgraph vs haversine vs Google Routes (accuracy + timing)
  osrm_time_dist_comparisons.py         # OSRM query timing for 3 city pairs (matches time_dist_comparisons)
  osrm_time_tests.py                    # OSRM query timing for 120 city pairs (matches geo_time_comparison_tests)
  path_algorithm_time_tests.py          # Compare scgraph vs NetworkX vs igraph across geographs and grids
  time_dist_comparisons.py              # Compare OSMNx+NX, OSMNx+scgraph, world_highways, Google Routes
  misc/
    cambridge_map_generator.py          # Generates route comparison PNGs for Cambridge/Somerville locations
    geo_time_comparison_tests_analysis.ipynb  # Jupyter analysis of geo_time_comparison_tests output
    geojsons_for_pictures.py            # Export all built-in geographs as GeoJSON for visualization
    osrm_setup.sh                       # Pull Docker image, download US OSM data, preprocess, start servers
    osrm_start.sh                       # Start OSRM servers (after one-time setup)
    osrm_data/                          # Created by osrm_setup.sh — ~20-30 GB, not committed
      us-latest.osm.pbf                 # Downloaded US OSM data
      us-latest.osrm*                   # Processed OSRM graph files
  utils/
    graphs.py                           # Graph conversion helpers (scgraph → NX, scgraph → igraph, OSMNx → scgraph)
    solvers.py                          # Timing-wrapped solver functions + OSMNx graph builder + Google API call
outputs/
  algorithm_tests.csv
  cambridge_osmnx_scgraph_comparison.csv
  geo_time_comparison_tests.csv
  osrm_setup_timing.json
  osrm_time_dist_comparisons.csv
  osrm_time_tests.csv
  path_algorithm_time_tests.csv
  time_dist_comparisons.csv
keys.json                               # API keys (gitignored); see setup below
pyproject.toml
```

---

## Environment Setup

```bash
uv sync
```

Key dependencies: `scgraph`, `networkx`, `igraph`, `osmnx`, `pamda`, `requests`, `polyline`, `matplotlib`

---

## Running Benchmarks

Run any script from the repo root:

```bash
uv run benchmarks/algorithm_tests.py
uv run benchmarks/geo_time_comparison_tests.py
uv run benchmarks/path_algorithm_time_tests.py
uv run benchmarks/time_dist_comparisons.py
uv run benchmarks/cambridge_osmnx_scgraph_comparison.py
```

Each script prints progress to stdout and writes results to `outputs/<script_name>.csv`.

### OSRM Benchmarks (requires Docker)

OSRM needs a one-time setup before either OSRM script will run. The setup script downloads ~9 GB of OSM data, preprocesses it for both CH and MLD algorithms (can take 30+ minutes on US data), and starts two servers.

```bash
# Step 1 — one-time setup (leaves both servers running)
./benchmarks/misc/osrm_setup.sh

# Step 2 — run either or both benchmark scripts
uv run benchmarks/osrm_time_tests.py
uv run benchmarks/osrm_time_dist_comparisons.py

# Step 3 — stop both servers when done
docker stop osrm_server_ch osrm_server_mld
```

`osrm_setup.sh` writes `outputs/osrm_setup_timing.json` with step durations (pull, download, extract, contract, partition, customize, ch_startup, mld_startup). Both OSRM scripts read that file to embed setup costs in their output CSVs.

To restart previously preprocessed servers without re-downloading data:

```bash
./benchmarks/misc/osrm_start.sh
```

---

## Script Details

### `algorithm_tests.py`
Tests every `scgraph` algorithm on 7 built-in geographs against 10 US coastal cities (100 city-pairs). Measures:
- One-time build times: `create_contraction_hierarchy`, `create_tnr_hierarchy`
- `distance_matrix` first and second pass (second pass benefits from cached shortest path trees)
- Per-algorithm first + second pass totals and averages across all 100 pairs

Algorithms tested: `dijkstra`, `a_star`, `bmssp`, `bellman_ford`, `dijkstra_buckets`, `cached_shortest_path`, `contraction_hierarchy`, `tnr`

Geographs tested: `marnet`, `oak_ridge_maritime`, `north_america_rail`, `us_freeway`, `world_highways_and_marnet`, `world_highways`, `world_railways`

### `cambridge_osmnx_scgraph_comparison.py`
Compares `scgraph` vs OSMNx vs Google Routes for bicycle routing on the Cambridge/Somerville, MA bike network. For each of 56 ordered pairs of 8 local landmarks:
- OSMNx graph downloaded via `osmnx.graph_from_place`, with edge speeds and travel times added
- Two GeoGraphs built from OSMNx: one weighted by `travel_time`, one by `length`
- Each pair is solved four ways: scgraph time-optimized, scgraph distance-optimized, OSMNx time-optimized, OSMNx distance-optimized
- Google Routes API queried for bicycle routing (requires `keys.json`)

Output: `outputs/cambridge_osmnx_scgraph_comparison.csv`

### `geo_time_comparison_tests.py`
Compares routing distance accuracy and speed for all unique pairs of 16 US cities using:
- `scgraph` world_highways
- `scgraph` us_freeway
- Haversine
- Haversine × 1.2 circuity
- Google Routes API (driving, traffic-unaware)

**Google API hack:** The script has a block that reloads previous Google results from the CSV to avoid re-hitting the API. To run live Google fetches, uncomment `test_google` in the function list and remove the reload hack block.

### `path_algorithm_time_tests.py`
Head-to-head timing of `scgraph` vs `NetworkX` vs `igraph` on 4 test cases per graph, 10 iterations each (`pamda_timer`). Graph types:
- `GeoGraph`: all 7 built-in geographs (4 fixed node-index test cases each)
- `GridGraph`: 9 sizes from 100×100 to 100×6400 plus 300×300 (center-column wall, 4 corner/diagonal test cases)

For GeoGraphs, also times one-time CH and TNR preprocessing.

Algorithms compared: NX Dijkstra, igraph shortest path, scgraph Dijkstra, scgraph A\*, scgraph Dijkstra Buckets, scgraph BMSSP, scgraph Bellman-Ford, scgraph CH (GeoGraph only), scgraph TNR (GeoGraph only)

### `time_dist_comparisons.py`
Tests 3 city pairs (LA→SD, ORL→TAM, NYC→PHI) across solvers with separate data-prep and solve timing:
- Data prep: `build_osmnx_graph` (one-time), `make_scgraph_from_osmnx` (one-time)
- Solve (10 iterations each): OSMNx+NX, OSMNx+scgraph, world_highways scgraph, US Freeway scgraph, Google Routes

### `osrm_setup.sh`
Shell script that runs the full OSRM setup pipeline and starts two HTTP servers. Each stage is timed independently:

| Stage | What it does |
|---|---|
| `osrm_pull` | `docker pull osrm/osrm-backend` |
| `osrm_download` | `wget` US OSM PBF from Geofabrik (~9 GB) |
| `osrm_extract` | `osrm-extract -p /opt/car.lua` (car/driving profile) |
| `osrm_contract` | `osrm-contract` (Contraction Hierarchies preprocessing) |
| `osrm_partition` | `osrm-partition` (MLD preprocessing step 1 of 2) |
| `osrm_customize` | `osrm-customize` (MLD preprocessing step 2 of 2) |
| `osrm_ch_startup` | `osrm-routed --algorithm ch` on port 5000 + poll until ready |
| `osrm_mld_startup` | `osrm-routed --algorithm mld` on port 5001 + poll until ready |

All timings are written to `outputs/osrm_setup_timing.json`. OSM data and processed files are stored in `benchmarks/misc/osrm_data/`. Both servers stay running after the script exits.

### `osrm_time_tests.py`
Queries both OSRM servers (CH on port 5000, MLD on port 5001) for all 120 unique pairs of the same 16 US cities used in `geo_time_comparison_tests.py`. Outputs `outputs/osrm_time_tests.csv` with per-pair query time and distance for each algorithm plus all one-time setup costs as repeated columns (so the CSV is self-contained for analysis).

Requires both OSRM servers to be running and `outputs/osrm_setup_timing.json` to exist.

### `osrm_time_dist_comparisons.py`
Tests the same 3 city pairs as `time_dist_comparisons.py` (LA→SD, ORL→TAM, NYC→PHI) using both OSRM algorithms. Output schema matches `time_dist_comparisons.csv` exactly, enabling direct comparison:
- One-time global setup costs appear as `category=setup`, `combination=global` rows
- Per-combination solve timing uses `pamda_timer` with 10 iterations (`category=network_solve`), with separate rows for `solver=osrm_ch` and `solver=osrm_mld`

Requires both OSRM servers to be running and `outputs/osrm_setup_timing.json` to exist.

### `misc/cambridge_map_generator.py`
Generates 56 side-by-side route comparison PNGs (one per ordered pair of 8 Cambridge/Somerville landmarks), saved to `outputs/cambridge/`. Each image overlays three routes on the OSMNx bike graph:
- Blue: scgraph time-optimized path
- Green: scgraph distance-optimized path
- Red: Google Routes bicycle path

Requires `keys.json` with a valid `google_api_key`.

### `misc/geojsons_for_pictures.py`
Loads all 7 built-in scgraph geographs and exports each as a compact GeoJSON file to `geojsons/` at the repo root.

---

## `utils/` Helpers

**`utils/graphs.py`**
- `make_nxgraph(graph)` — scgraph adjacency list → NetworkX Graph
- `igraph_from_scgraph(graph)` — scgraph adjacency list → igraph Graph (undirected)
- `igraph_from_osmnx(osmnx_graph)` — OSMNx graph → igraph Graph
- `make_gridgraph(x_size, y_size)` — creates a GridGraph with a center-column wall (blocks rows 5+) and a 2×2 shape
- `get_nx_shortest_path(graph, origin, destination)` — runs `dijkstra_predecessor_and_distance`
- `get_igraph_shortest_path(graph, origin, destination)` — returns `{path, length}`
- `make_scgraph_from_osmnx(osmnx_graph)` — wraps `GeoGraph.load_from_osmnx_graph`

**`utils/solvers.py`**
- `test_google(coord1, coord2)` — calls Google Routes API v2, returns km (requires `keys.json`)
- `test_world_highways_scgraph(coord1, coord2)` — scgraph world_highways with `off_graph_circuity=1.2`
- `test_us_freeway_scgraph(coord1, coord2)` — scgraph us_freeway with `off_graph_circuity=1.2`
- `test_haversine(coord1, coord2)` — raw haversine in km
- `test_haversine_circuity(coord1, coord2)` — haversine × 1.2 circuity
- `build_osmnx_graph(coord1, coord2, buffer_km=50)` — downloads OSMNx graph (motorway/trunk/primary only) around midpoint with buffer
- `solve_nx_on_osmnx(G, coord1, coord2)` — NX shortest path on pre-built OSMNx graph
- `solve_scgraph_on_osmnx(geograph, coord1, coord2)` — scgraph `get_shortest_path` on converted GeoGraph

**`keys.json`** (repo root, gitignored)
```json
{
    "google_api_key": "YOUR_API_KEY"
}
```
Required only for Google Routes tests. Google Routes API must be enabled in the Google Cloud console.

---

## Output Schema (CSV columns per script)

**`algorithm_tests.csv`**: `function`, `unit`, `time`, `avg_time_per_dist`, `graph`

**`cambridge_osmnx_scgraph_comparison.csv`**: `origin`, `destination`, `scgraph_time_optimized_distance_km`, `scgraph_time_optimized_time_seconds`, `scgraph_time_optimized_duration_seconds`, `osmnx_time_optimized_distance_km`, `osmnx_time_optimized_time_seconds`, `osmnx_time_optimized_duration_seconds`, `scgraph_distance_optimized_distance_km`, `scgraph_distance_optimized_time_seconds`, `scgraph_distance_optimized_duration_seconds`, `osmnx_distance_optimized_distance_km`, `osmnx_distance_optimized_time_seconds`, `osmnx_distance_optimized_duration_seconds`, `google_distance_km`, `google_time_seconds`, `google_duration_seconds`

**`geo_time_comparison_tests.csv`**: `city1`, `city2`, `coord1`, `coord2`, `<solver>_time_ms`, `<solver>_length_km` for each solver

**`path_algorithm_time_tests.csv`**: `graph_name`, `case_name`, `graph_nodes`, `graph_edges`, `node_steps_needed`, `sc_ch_build_ms`, `sc_tnr_build_ms`, `nx_dijkstra_time_ms`, `ig_shortest_path_time_ms`, `sc_dijkstra_modified_time_ms`, `sc_a_star_time_ms`, `sc_dijkstra_buckets_time_ms`, `sc_bmssp_time_ms`, `sc_bellman_ford_time_ms`, `sc_ch_time_ms`, `sc_tnr_time_ms`, `nx_dijkstra_stdev`, `ig_shortest_path_stdev`, `sc_dijkstra_modified_stdev`, `sc_a_star_stdev`, `sc_dijkstra_buckets_stdev`, `sc_bmssp_stdev`, `sc_bellman_ford_stdev`, `sc_ch_stdev`, `sc_tnr_stdev`

**`time_dist_comparisons.csv`**: `module`, `function`, `unit`, `iterations`, `avg`, `min`, `max`, `std`, `combination`, `category`, `solver`, `distance_km`

**`osrm_time_tests.csv`**: `city1`, `city2`, `coord1`, `coord2`, `test_osrm_ch_time_ms`, `test_osrm_ch_length_km`, `test_osrm_mld_time_ms`, `test_osrm_mld_length_km`, `osrm_pull_ms`, `osrm_download_ms`, `osrm_extract_ms`, `osrm_contract_ms`, `osrm_partition_ms`, `osrm_customize_ms`, `osrm_ch_startup_ms`, `osrm_mld_startup_ms`

**`osrm_time_dist_comparisons.csv`**: same schema as `time_dist_comparisons.csv` — `module`, `function`, `unit`, `iterations`, `avg`, `min`, `max`, `std`, `combination`, `category`, `solver`, `distance_km` — with `solver` values of `osrm_ch` and `osrm_mld`

---

## Key Notes

- Coordinates are always `(latitude, longitude)` tuples (not dicts) in `utils/`; scgraph `get_shortest_path` expects `{"latitude": ..., "longitude": ...}` dicts — the solvers handle this conversion.
- `pamda_timer` wraps a function and exposes `.get_time_stats(**kwargs)` returning `{avg, min, max, std}` in ms.
- `scgraph` geographs are loaded once at module import in `utils/solvers.py` and reused across all calls — this amortizes the download/load cost.
- The `geo_time_comparison_tests.ipynb` notebook shows that `scgraph` world_highways and us_freeway achieve ~4% MAPE vs Google Routes and ~0.99 R², while raw haversine is ~14% MAPE.
- OSRM uses **longitude, latitude** order (GeoJSON convention) — the opposite of scgraph's `(latitude, longitude)` tuples. The OSRM scripts handle this conversion internally.
- OSRM's `osrm-contract` (CH preprocessing) is the fair apples-to-apples comparison for scgraph's `create_contraction_hierarchy`. Both use the same underlying algorithm family.
- OSRM's MLD (Multi-Level Dijkstra) uses `osrm-partition` + `osrm-customize` preprocessing and runs on port 5001. It is a hierarchical Dijkstra variant — faster than plain Dijkstra but different in approach from CH.
- `benchmarks/misc/osrm_data/` is large (~20–30 GB) and should not be committed. `outputs/osrm_setup_timing.json` is small and safe to commit if you want to preserve timing results without re-running setup.
- All scripts must be run from the **repo root** (e.g., `uv run benchmarks/algorithm_tests.py`). Relative paths in scripts (for `keys.json`, `outputs/`, etc.) are relative to the working directory, not the script file.
