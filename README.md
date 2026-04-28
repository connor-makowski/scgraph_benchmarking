# SCGraph Benchmarking

This repo is not intended to be used by end users and is purely for internal and development purposes related to the SCGraph package and associated packages.
- It is not designed to be used as a library
- It is designed to be used as a collection of scripts to benchmark the performance of the SCGraph library against other libraries like NetworkX and OSMNX. 

This directory contains scripts and configurations for benchmarking the SCGraph library. 
- The benchmarks are designed to evaluate the performance of various graph algorithms implemented in SCGraph. 
- It also includes benchmarking against other libraries like NetworkX and OSMNX.

## Environment Setup
Setup a virtual environment and install the required dependencies:

```bash
python3.13 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

## Running Benchmarks

### Notes for Google Routes API
If you want to evaluate the performance of Google Routes API, you will have to enable the Routes API in the google dashboard and set the API key in `utils/keys.json` file. The file should look like this:

```json
{
    "google_api_key": "YOUR_API_KEY"
}
```

You should also modify the `geo_time_comparisons_test.py` script to actually fetch the data from Google Routes API live rather than reloading the data from the same test when previously run.

### Benchmark Scripts

To run the benchmarks, execute the desired benchmark script. For example, to run the distance matrix benchmark:

```bash
python geo_time_comparison_tests.py
```

### Output
The output of the benchmarks will be saved in the `outputs` directory. Each benchmark script will generate a file containing the results of the benchmark, including execution times and any relevant metrics.

---

## OSRM Benchmarks

Two additional scripts benchmark [OSRM](http://project-osrm.org/) (Open Source Routing Machine) using Docker.
OSRM requires a one-time setup before running either script.

> **Disk space:** `osrm_data/` will use approximately 20–30 GB for the US OSM extract and processed files.

### Setup (run once)

```bash
./osrm_setup.sh
```

This script:
1. Pulls the `osrm/osrm-backend` Docker image
2. Downloads `us-latest.osm.pbf` from Geofabrik (~9 GB)
3. Runs `osrm-extract` with the car profile
4. Runs `osrm-contract` (Contraction Hierarchies)
5. Starts the OSRM HTTP server on `localhost:5000`

All step durations are written to `outputs/osrm_setup_timing.json` for use by the benchmark scripts.

### Running OSRM Benchmarks

With the server running, execute either script:

```bash
# 120 unique pairs of 16 US cities — per-pair query time + distance
python osrm_time_tests.py

# Same 3 city pairs as time_dist_comparisons.py — 10-iteration query timing
python osrm_time_dist_comparisons.py
```

### Stopping the Server

```bash
docker stop osrm_server_ch osrm_server_mld
```
