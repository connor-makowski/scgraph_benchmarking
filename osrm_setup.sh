#!/bin/bash
# OSRM setup script: pull image, download US OSM data, preprocess, start servers.
# Runs full preprocessing for both CH (Contraction Hierarchies) and MLD (Multi-Level
# Dijkstra), then starts both servers: CH on localhost:5000, MLD on localhost:5001.
# All major steps are timed and written to outputs/osrm_setup_timing.json.
#
# After this script exits:
#   CH  server: http://localhost:5000
#   MLD server: http://localhost:5001
# Run `python osrm_time_tests.py` next.
# Stop servers with: docker stop osrm_server_ch osrm_server_mld
#
# Disk space warning: US OSM data + processed files require ~20-30 GB.

set -e

DATA_DIR="$(pwd)/osrm_data"
OSM_FILE="us-latest.osm.pbf"
OSM_URL="https://download.geofabrik.de/north-america/us-latest.osm.pbf"
OSRM_BASE="${OSM_FILE%.osm.pbf}.osrm"
IMAGE="osrm/osrm-backend"

mkdir -p "$DATA_DIR"

# Stop any existing servers from a prior run
docker stop osrm_server_ch  2>/dev/null && echo "Stopped existing osrm_server_ch container."  || true
docker stop osrm_server_mld 2>/dev/null && echo "Stopped existing osrm_server_mld container." || true

# ── 1. Pull Docker image ──────────────────────────────────────────────────────
echo ""
echo "[1/8] Pulling Docker image: $IMAGE ..."
t0=$(date +%s%3N)
docker pull "$IMAGE"
t1=$(date +%s%3N)
pull_ms=$((t1 - t0))
echo "      Done: ${pull_ms} ms"

# ── 2. Download OSM data ──────────────────────────────────────────────────────
echo ""
echo "[2/8] Downloading OSM data from Geofabrik (~9 GB) ..."
t0=$(date +%s%3N)
wget -q --show-progress -O "$DATA_DIR/$OSM_FILE" "$OSM_URL"
t1=$(date +%s%3N)
download_ms=$((t1 - t0))
echo "      Done: ${download_ms} ms"

# ── 3. Extract (osrm-extract with car profile) ────────────────────────────────
echo ""
echo "[3/8] Running osrm-extract (car profile) ..."
t0=$(date +%s%3N)
docker run --rm \
  -v "$DATA_DIR:/data" \
  "$IMAGE" \
  osrm-extract -p /opt/car.lua /data/$OSM_FILE
t1=$(date +%s%3N)
extract_ms=$((t1 - t0))
echo "      Done: ${extract_ms} ms"

# ── 4. Contract (CH preprocessing) ───────────────────────────────────────────
echo ""
echo "[4/8] Running osrm-contract (Contraction Hierarchies preprocessing) ..."
t0=$(date +%s%3N)
docker run --rm \
  -v "$DATA_DIR:/data" \
  "$IMAGE" \
  osrm-contract /data/$OSRM_BASE
t1=$(date +%s%3N)
contract_ms=$((t1 - t0))
echo "      Done: ${contract_ms} ms"

# ── 5. Partition (MLD preprocessing — step 1 of 2) ───────────────────────────
echo ""
echo "[5/8] Running osrm-partition (Multi-Level Dijkstra step 1 of 2) ..."
t0=$(date +%s%3N)
docker run --rm \
  -v "$DATA_DIR:/data" \
  "$IMAGE" \
  osrm-partition /data/$OSRM_BASE
t1=$(date +%s%3N)
partition_ms=$((t1 - t0))
echo "      Done: ${partition_ms} ms"

# ── 6. Customize (MLD preprocessing — step 2 of 2) ───────────────────────────
echo ""
echo "[6/8] Running osrm-customize (Multi-Level Dijkstra step 2 of 2) ..."
t0=$(date +%s%3N)
docker run --rm \
  -v "$DATA_DIR:/data" \
  "$IMAGE" \
  osrm-customize /data/$OSRM_BASE
t1=$(date +%s%3N)
customize_ms=$((t1 - t0))
echo "      Done: ${customize_ms} ms"

# ── 7. Start CH server (port 5000) ────────────────────────────────────────────
echo ""
echo "[7/8] Starting OSRM CH server (port 5000) ..."
t0=$(date +%s%3N)
docker run -d --rm \
  -p 5000:5000 \
  --name osrm_server_ch \
  -v "$DATA_DIR:/data" \
  "$IMAGE" \
  osrm-routed --algorithm ch /data/$OSRM_BASE

PROBE_CH="http://localhost:5000/route/v1/driving/-118.2437,34.0522;-74.006,40.7128?overview=false"
echo "      Waiting for CH server to be ready ..."
until curl -sf "$PROBE_CH" > /dev/null 2>&1; do
  sleep 1
done
t1=$(date +%s%3N)
ch_startup_ms=$((t1 - t0))
echo "      Ready: ${ch_startup_ms} ms"

# ── 8. Start MLD server (port 5001) ──────────────────────────────────────────
echo ""
echo "[8/8] Starting OSRM MLD server (port 5001) ..."
t0=$(date +%s%3N)
docker run -d --rm \
  -p 5001:5000 \
  --name osrm_server_mld \
  -v "$DATA_DIR:/data" \
  "$IMAGE" \
  osrm-routed --algorithm mld /data/$OSRM_BASE

PROBE_MLD="http://localhost:5001/route/v1/driving/-118.2437,34.0522;-74.006,40.7128?overview=false"
echo "      Waiting for MLD server to be ready ..."
until curl -sf "$PROBE_MLD" > /dev/null 2>&1; do
  sleep 1
done
t1=$(date +%s%3N)
mld_startup_ms=$((t1 - t0))
echo "      Ready: ${mld_startup_ms} ms"

# ── Write timing JSON ─────────────────────────────────────────────────────────
cat > "$DATA_DIR/setup_timing.json" << EOF
{
  "pull_ms": $pull_ms,
  "download_ms": $download_ms,
  "extract_ms": $extract_ms,
  "contract_ms": $contract_ms,
  "partition_ms": $partition_ms,
  "customize_ms": $customize_ms,
  "ch_startup_ms": $ch_startup_ms,
  "mld_startup_ms": $mld_startup_ms
}
EOF

echo ""
echo "========================================"
echo "OSRM setup complete"
echo "  Image pull:       ${pull_ms} ms"
echo "  OSM download:     ${download_ms} ms"
echo "  osrm-extract:     ${extract_ms} ms"
echo "  osrm-contract:    ${contract_ms} ms"
echo "  osrm-partition:   ${partition_ms} ms"
echo "  osrm-customize:   ${customize_ms} ms"
echo "  CH  server ready: ${ch_startup_ms} ms"
echo "  MLD server ready: ${mld_startup_ms} ms"
echo "========================================"
echo ""
echo "CH  server running at http://localhost:5000"
echo "MLD server running at http://localhost:5001"
echo "Next step:  python osrm_time_tests.py"
echo "To stop:    docker stop osrm_server_ch osrm_server_mld"
