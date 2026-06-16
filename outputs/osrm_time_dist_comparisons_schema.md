# osrm_time_dist_comparisons.csv — Field Reference

Tests both OSRM algorithms (CH and MLD) on the same 3 city pairs used in `time_dist_comparisons` (LA→SD, ORL→TAM, NYC→PHI). Uses the same long/tidy schema as `time_dist_comparisons.csv` to enable direct comparison. Network solve rows use 10 iterations via `pamda_timer`.

---

## Fields

| Field | Description |
|---|---|
| `module` | Python module where the timed function lives (e.g. `osrm_setup`, `osrm_solver`) |
| `function` | Name of the function or setup stage that was timed |
| `unit` | Time unit — always `ms` |
| `iterations` | Number of timing iterations (`1` for setup/data_prep, `10` for network_solve) |
| `avg` | Average time (ms) across iterations |
| `min` | Minimum time (ms) across iterations |
| `max` | Maximum time (ms) across iterations |
| `std` | Standard deviation (ms) across iterations |
| `combination` | City-pair abbreviation (`LA_SD`, `ORL_TAM`, `NYC_PHI`) or `global` for setup rows |
| `category` | Row type: `setup` (global one-time OSRM pipeline) or `network_solve` (per-query solve) |
| `solver` | Solver identifier (see table below) |
| `distance_km` | Route distance (km); blank for `setup` rows |

---

## `category` values

| `category` | Description |
|---|---|
| `setup` | Global one-time OSRM pipeline cost (pull, download, extract, preprocess, start servers); `combination=global` |
| `network_solve` | Per-query solve cost averaged over 10 iterations for a specific city pair |

---

## `solver` values

| `solver` | Description |
|---|---|
| `osrm_ch` | OSRM Contraction Hierarchies server (port 5000) |
| `osrm_mld` | OSRM Multi-Level Dijkstra server (port 5001) |
| `osrm_pull` | Docker image pull stage (setup row only) |
| `osrm_download` | US OSM PBF download stage (setup row only) |
| `osrm_extract` | `osrm-extract` preprocessing stage (setup row only) |
| `osrm_contract` | `osrm-contract` CH preprocessing stage (setup row only) |
| `osrm_partition` | `osrm-partition` MLD preprocessing step 1 (setup row only) |
| `osrm_customize` | `osrm-customize` MLD preprocessing step 2 (setup row only) |
| `osrm_ch_startup` | CH server startup + readiness poll (setup row only) |
| `osrm_mld_startup` | MLD server startup + readiness poll (setup row only) |

---

## Notes

- This file uses the identical schema as `time_dist_comparisons.csv` — the two CSVs can be unioned for cross-solver analysis.
- Setup rows have `combination=global` because OSRM preprocessing is not per city-pair; the cost is shared across all queries.
- `osrm_contract` is the fair comparison for scgraph's `create_contraction_hierarchy` (both implement the same algorithm family).
- OSRM MLD uses `osrm-partition` + `osrm-customize` together — both stages are needed and both appear as separate setup rows.
