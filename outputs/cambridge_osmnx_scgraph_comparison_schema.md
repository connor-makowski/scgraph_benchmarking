# cambridge_osmnx_scgraph_comparison.csv — Field Reference

All routes are computed on a **bike network** for Somerville and Cambridge, MA.  
"Duration" fields are wall-clock solve time, not travel time.

---

## Identifiers

| Field | Description |
|---|---|
| `origin` | Name of the starting location |
| `destination` | Name of the ending location |

---

## scgraph — time-optimized

Shortest path minimizing **travel time** using scgraph on the OSMNx-derived GeoGraph.  
Distance is back-calculated by re-walking the same path on the distance-weighted GeoGraph.

| Field | Description |
|---|---|
| `scgraph_time_optimized_distance_km` | Distance (km) of the time-optimal path |
| `scgraph_time_optimized_time_seconds` | Travel time (s) of the time-optimal path |
| `scgraph_time_optimized_duration_seconds` | Wall-clock time (s) for scgraph to compute the path |

---

## osmnx — time-optimized

Shortest path minimizing **travel time** using NetworkX on the raw OSMNx graph.  
Distance is summed from edge `length` attributes along the returned path.

| Field | Description |
|---|---|
| `osmnx_time_optimized_distance_km` | Distance (km) of the time-optimal path |
| `osmnx_time_optimized_time_seconds` | Travel time (s) of the time-optimal path |
| `osmnx_time_optimized_duration_seconds` | Wall-clock time (s) for osmnx to compute the path (includes nearest-node lookup) |

---

## scgraph — distance-optimized

Shortest path minimizing **distance** using scgraph on the OSMNx-derived GeoGraph.  
Travel time is back-calculated by re-walking the same path on the time-weighted GeoGraph.

| Field | Description |
|---|---|
| `scgraph_distance_optimized_distance_km` | Distance (km) of the distance-optimal path |
| `scgraph_distance_optimized_time_seconds` | Travel time (s) of the distance-optimal path |
| `scgraph_distance_optimized_duration_seconds` | Wall-clock time (s) for scgraph to compute the path |

---

## osmnx — distance-optimized

Shortest path minimizing **distance** using NetworkX on the raw OSMNx graph.  
Travel time is summed from edge `travel_time` attributes along the returned path.

| Field | Description |
|---|---|
| `osmnx_distance_optimized_distance_km` | Distance (km) of the distance-optimal path |
| `osmnx_distance_optimized_time_seconds` | Travel time (s) of the distance-optimal path |
| `osmnx_distance_optimized_duration_seconds` | Wall-clock time (s) for osmnx to compute the path (includes nearest-node lookup) |

---

## google — bicycle routing

Google Routes API v2 (`travelMode: BICYCLE`). No traffic-awareness setting is applied (not supported for bicycle mode). This is used as a real-world ground-truth reference for both distance and time.

| Field | Description |
|---|---|
| `google_distance_km` | Distance (km) returned by Google Routes API |
| `google_time_seconds` | Travel time (s) returned by Google Routes API |
| `google_duration_seconds` | Wall-clock time (s) for the API round-trip |

---

## Notes

- Travel times in the OSMNx/scgraph solvers are derived from OSMNx-assigned edge speeds (`ox.add_edge_speeds` / `ox.add_edge_travel_times`) and may differ from Google's real-world cycling estimates.
- The time-optimized and distance-optimized paths are generally different routes; their cross-metric values (e.g. time of the distance-optimal path) show the trade-off between the two objectives.
- `duration_seconds` fields measure solver latency only — graph loading and GeoGraph construction happen once before the loop and are not included.
