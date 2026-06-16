# osrm_time_tests.csv — Field Reference

Queries both OSRM servers (CH on port 5000, MLD on port 5001) for all 120 unique pairs of 16 US cities (the same city set used in `geo_time_comparison_tests`). Each row is one directed city pair. One-time setup costs are repeated on every row so the CSV is self-contained for analysis.

---

## Identifiers

| Field | Description |
|---|---|
| `city1` | Name of the origin city |
| `city2` | Name of the destination city |
| `coord1` | `(latitude, longitude)` of the origin city |
| `coord2` | `(latitude, longitude)` of the destination city |

---

## Per-query Results

| Field | Description |
|---|---|
| `test_osrm_ch_time_ms` | Query time (ms) for OSRM Contraction Hierarchies (port 5000) |
| `test_osrm_ch_length_km` | Route distance (km) returned by OSRM CH |
| `test_osrm_mld_time_ms` | Query time (ms) for OSRM Multi-Level Dijkstra (port 5001) |
| `test_osrm_mld_length_km` | Route distance (km) returned by OSRM MLD |

---

## One-time Setup Costs (repeated on every row)

These are the step durations from `outputs/osrm_setup_timing.json`, written by `osrm_setup.sh`. Values are the same on every row.

| Field | Description |
|---|---|
| `osrm_pull_ms` | Time (ms) to `docker pull osrm/osrm-backend` |
| `osrm_download_ms` | Time (ms) to download the US OSM PBF file (~9 GB) from Geofabrik |
| `osrm_extract_ms` | Time (ms) for `osrm-extract` with the car/driving profile |
| `osrm_contract_ms` | Time (ms) for `osrm-contract` (CH preprocessing) |
| `osrm_partition_ms` | Time (ms) for `osrm-partition` (MLD preprocessing step 1) |
| `osrm_customize_ms` | Time (ms) for `osrm-customize` (MLD preprocessing step 2) |
| `osrm_ch_startup_ms` | Time (ms) to start the CH server and poll until ready |
| `osrm_mld_startup_ms` | Time (ms) to start the MLD server and poll until ready |

---

## Notes

- OSRM uses longitude-first coordinate order (GeoJSON convention) — the opposite of scgraph's `(latitude, longitude)` tuples. The script handles this conversion internally.
- `osrm_contract` is the fair apples-to-apples comparison for scgraph's `create_contraction_hierarchy`.
- Setup costs are repeated per row (not aggregated) so that any subset of rows remains self-contained for cost analysis.
