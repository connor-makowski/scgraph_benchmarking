# scgraph_benchmarking: Development Guide

## Project Purpose

This is a benchmarking and analysis repo for the [`scgraph`](https://github.com/connor-makowski/scgraph) library. It is **not** a library itself — it is a collection of standalone scripts used to:

- Benchmark `scgraph` algorithms (Dijkstra, A\*, BMSSP, CH, TNR, cached) across built-in geographs
- Compare `scgraph` performance against `NetworkX` and `igraph`
- Compare routing accuracy and timing against Google Routes API
- Compare `scgraph` solving on OSMNx graphs vs. NetworkX on the same OSMNx graphs
- Benchmark OSRM (Docker-based) for setup/preprocessing time and per-query performance

Results are written to CSV files in `outputs/` and analyzed in a Jupyter notebook.

---

## Directory Layout

```
algorithm_tests.py                    # Benchmark all scgraph algorithms per geograph (first + second pass)
geo_time_comparison_tests.py          # Compare scgraph vs haversine vs Google Routes (accuracy + timing)
path_algorithm_time_tests.py          # Compare scgraph vs NetworkX vs igraph (10 iterations each)
time_dist_comparisons.py              # Compare OSMNx+NX, OSMNx+scgraph, world_highways, Google Routes
osrm_setup.sh                         # Pull Docker image, download US OSM data, preprocess, start server
osrm_time_tests.py                    # OSRM query timing for 120 city pairs (matches geo_time_comparison_tests)
osrm_time_dist_comparisons.py         # OSRM query timing for 3 city pairs (matches time_dist_comparisons)
geo_time_comparison_tests_analysis.ipynb  # Jupyter analysis of geo_time_comparison_tests output
misc/
  geojsons_for_pictures.py            # Export all built-in geographs as GeoJSON for visualization
osrm_data/                            # Created by osrm_setup.sh — ~20-30 GB, not committed
  us-latest.osm.pbf                   # Downloaded US OSM data
  us-latest.osrm*                     # Processed OSRM graph files
  setup_timing.json                   # Step durations written by osrm_setup.sh
outputs/
  algorithm_tests.csv
  geo_time_comparison_tests.csv
  osrm_time_tests.csv
  osrm_time_dist_comparisons.csv
  path_algorithm_time_tests.csv
  time_dist_comparisons.csv
utils/
  graphs.py                           # Graph conversion helpers (scgraph → NX, scgraph → igraph, OSMNx → scgraph)
  solvers.py                          # Timing-wrapped solver functions + OSMNx graph builder + Google API call
  keys.json                           # API keys (gitignored); see setup below
requirements.txt
```

---

## Environment Setup

```bash
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Key dependencies: `scgraph`, `networkx`, `igraph`, `osmnx`, `pamda`, `requests`

---

## Running Benchmarks

Run any script from the repo root:

```bash
python algorithm_tests.py
python geo_time_comparison_tests.py
python path_algorithm_time_tests.py
python time_dist_comparisons.py
```

Each script prints progress to stdout and writes results to `outputs/<script_name>.csv`.

### OSRM Benchmarks (requires Docker)

OSRM needs a one-time setup before either OSRM script will run. The setup script downloads ~9 GB of OSM data, preprocesses it for both CH and MLD algorithms (can take 30+ minutes on US data), and starts two servers.

```bash
# Step 1 — one-time setup (leaves both servers running)
./osrm_setup.sh

# Step 2 — run either or both benchmark scripts
python osrm_time_tests.py
python osrm_time_dist_comparisons.py

# Step 3 — stop both servers when done
docker stop osrm_server_ch osrm_server_mld
```

`osrm_setup.sh` writes `outputs/osrm_setup_timing.json` with step durations (pull, download, extract, contract, partition, customize, ch_startup, mld_startup). Both OSRM scripts read that file to embed setup costs in their output CSVs.

---

## Script Details

### `algorithm_tests.py`
Tests every `scgraph` algorithm on 7 built-in geographs against 10 US coastal cities (100 city-pairs). Measures:
- One-time build times: `create_contraction_hierarchy`, `create_tnr_hierarchy`
- `distance_matrix` first and second pass (second pass benefits from cached shortest path trees)
- Per-algorithm first + second pass totals and averages across all 100 pairs

Algorithms tested: `dijkstra`, `a_star`, `cached_shortest_path`, `contraction_hierarchy`, `tnr`, `dijkstra_buckets`

Geographs tested: `marnet`, `oak_ridge_maritime`, `north_america_rail`, `us_freeway`, `world_highways_and_marnet`, `world_highways`, `world_railways`

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
- `GeoGraph`: World Highways, World Highways + Marnet, US Freeway (4 fixed node-pair test cases)
- `GridGraph`: various sizes from 100×100 up to 300×300 (with a vertical wall obstacle, 4 corner/diagonal test cases)

Algorithms compared: NX Dijkstra, igraph shortest path, scgraph Dijkstra, scgraph A\*, scgraph BMSSP

### `time_dist_comparisons.py`
Tests 3 city pairs (LA→SD, ORL→TAM, NYC→PHI) across solvers with separate data-prep and solve timing:
- Data prep: `build_osmnx_graph` (one-time), `make_scgraph_from_osmnx` (one-time)
- Solve: OSMNx+NX, OSMNx+scgraph, world_highways scgraph, US Freeway scgraph, Google Routes

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

All timings are written to `outputs/osrm_setup_timing.json`. Both servers stay running after the script exits.

### `osrm_time_tests.py`
Queries both OSRM servers (CH on port 5000, MLD on port 5001) for all 120 unique pairs of the same 16 US cities used in `geo_time_comparison_tests.py`. Outputs `outputs/osrm_time_tests.csv` with per-pair query time and distance for each algorithm plus all one-time setup costs as repeated columns (so the CSV is self-contained for analysis).

Requires both OSRM servers to be running and `outputs/osrm_setup_timing.json` to exist.

### `osrm_time_dist_comparisons.py`
Tests the same 3 city pairs as `time_dist_comparisons.py` (LA→SD, ORL→TAM, NYC→PHI) using both OSRM algorithms. Output schema matches `time_dist_comparisons.csv` exactly, enabling direct comparison:
- One-time global setup costs (pull, download, extract, contract, partition, customize, ch_startup, mld_startup) appear as `category=setup`, `combination=global` rows
- Per-combination solve timing uses `pamda_timer` with 10 iterations (`category=network_solve`), with separate rows for `solver=osrm_ch` and `solver=osrm_mld`

Requires both OSRM servers to be running and `outputs/osrm_setup_timing.json` to exist.

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
- `test_google(coord1, coord2)` — calls Google Routes API v2, returns km (requires key in `utils/keys.json`)
- `test_world_highways_scgraph(coord1, coord2)` — scgraph world_highways with `off_graph_circuity=1.2`
- `test_us_freeway_scgraph(coord1, coord2)` — scgraph us_freeway with `off_graph_circuity=1.2`
- `test_haversine(coord1, coord2)` — raw haversine in km
- `test_haversine_circuity(coord1, coord2)` — haversine × 1.2 circuity
- `build_osmnx_graph(coord1, coord2, buffer_km=50)` — downloads OSMNx graph (motorway/trunk/primary only) around midpoint with buffer
- `solve_nx_on_osmnx(G, coord1, coord2)` — NX shortest path on pre-built OSMNx graph
- `solve_scgraph_on_osmnx(geograph, coord1, coord2)` — scgraph `get_shortest_path` on converted GeoGraph

**`utils/keys.json`**
```json
{
    "google_api_key": "YOUR_API_KEY"
}
```
Required only for Google Routes tests. Google Routes API must be enabled in the Google Cloud console.

---

## Output Schema (CSV columns per script)

**`algorithm_tests.csv`**: `function`, `unit`, `time`, `avg_time_per_dist`, `graph`

**`geo_time_comparison_tests.csv`**: `city1`, `city2`, `coord1`, `coord2`, `<solver>_time_ms`, `<solver>_length_km` for each solver

**`path_algorithm_time_tests.csv`**: `graph_name`, `case_name`, `graph_nodes`, `graph_edges`, `node_steps_needed`, `<solver>_time_ms`, `<solver>_stdev` for each solver

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
- `osrm_data/` is large (~20–30 GB) and should not be committed. The `setup_timing.json` inside it is small and safe to commit if you want to preserve timing results without re-running setup.
