# SCGraph Benchmarking

A collection of scripts for benchmarking the [`scgraph`](https://github.com/connor-makowski/scgraph) library against NetworkX, igraph, OSMNx, OSRM, and the Google Routes API. Not intended as a library — see [DEVELOPMENT.md](DEVELOPMENT.md) for full details.

## Environment Setup

```bash
uv sync
```

## Running Benchmarks

```bash
uv run benchmarks/algorithm_tests.py
uv run benchmarks/geo_time_comparison_tests.py
uv run benchmarks/path_algorithm_time_tests.py
uv run benchmarks/time_dist_comparisons.py
uv run benchmarks/cambridge_osmnx_scgraph_comparison.py
```

All scripts write results to `outputs/`.

### Google Routes API

Some scripts call the Google Routes API. Enable the Routes API in your Google Cloud console and add your key to `keys.json` at the repo root:

```json
{
    "google_api_key": "YOUR_API_KEY"
}
```

---

## OSRM Benchmarks

Two scripts benchmark [OSRM](http://project-osrm.org/) via Docker and require a one-time setup.

> **Disk space:** `benchmarks/misc/osrm_data/` will use approximately 20–30 GB for the US OSM extract and processed files.

### Setup (run once)

```bash
./benchmarks/misc/osrm_setup.sh
```

This script downloads US OSM data (~9 GB), preprocesses it for both CH and MLD algorithms, starts both servers, and writes timing results to `outputs/osrm_setup_timing.json`.

### Running OSRM Benchmarks

With both servers running:

```bash
uv run benchmarks/osrm_time_tests.py
uv run benchmarks/osrm_time_dist_comparisons.py
```

### Stopping the Servers

```bash
docker stop osrm_server_ch osrm_server_mld
```
