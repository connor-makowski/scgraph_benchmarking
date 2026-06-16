# geo_time_comparison_tests.csv — Field Reference

Compares routing distance accuracy and solve speed across solvers for all unique pairs of 16 US cities. Each row is one directed city pair. Timing values are wall-clock solve time for a single query.

---

## Identifiers

| Field | Description |
|---|---|
| `city1` | Name of the origin city |
| `city2` | Name of the destination city |
| `coord1` | `(latitude, longitude)` of the origin city |
| `coord2` | `(latitude, longitude)` of the destination city |

---

## scgraph — World Highways

Shortest path on the built-in `world_highways` geograph with `off_graph_circuity=1.2`.

| Field | Description |
|---|---|
| `test_world_highways_scgraph_time_ms` | Solve time (ms) |
| `test_world_highways_scgraph_length_km` | Route distance (km) |

---

## scgraph — US Freeway

Shortest path on the built-in `us_freeway` geograph with `off_graph_circuity=1.2`.

| Field | Description |
|---|---|
| `test_us_freeway_scgraph_time_ms` | Solve time (ms) |
| `test_us_freeway_scgraph_length_km` | Route distance (km) |

---

## Haversine

Great-circle straight-line distance. No routing — purely geometric.

| Field | Description |
|---|---|
| `test_haversine_time_ms` | Compute time (ms) |
| `test_haversine_length_km` | Straight-line distance (km) |

---

## Haversine × 1.2 Circuity

Haversine distance scaled by a 1.2 circuity factor to approximate real-world road distance.

| Field | Description |
|---|---|
| `test_haversine_circuity_time_ms` | Compute time (ms) |
| `test_haversine_circuity_length_km` | Circuity-adjusted distance (km) |

---

## Google Routes API

Google Routes API v2 (`travelMode: DRIVE`, traffic-unaware). Used as ground-truth reference.

| Field | Description |
|---|---|
| `test_google_time_ms` | API round-trip time (ms) — includes network latency |
| `test_google_length_km` | Route distance (km) returned by Google |

---

## Notes

- Google results are often reloaded from a prior CSV run to avoid re-hitting the API. See the reload-hack block in `geo_time_comparison_tests.py`.
- Timing for haversine is near zero and not meaningful for latency comparisons — it exists for completeness.
