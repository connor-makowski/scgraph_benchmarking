#!/bin/bash
# Start the OSRM HTTP servers using preprocessed data from osrm_data/.
# Requires osrm_setup.sh to have been run at least once (both CH and MLD preprocessing).
#
#   CH  server: http://localhost:5000
#   MLD server: http://localhost:5001
# Stop with: docker stop osrm_server_ch osrm_server_mld

set -e

DATA_DIR="$(pwd)/osrm_data"
OSM_FILE="us-latest.osm.pbf"
OSRM_BASE="${OSM_FILE%.osm.pbf}.osrm"
IMAGE="osrm/osrm-backend"

if [ ! -f "$DATA_DIR/$OSRM_BASE" ]; then
  echo "Error: $DATA_DIR/$OSRM_BASE not found. Run osrm_setup.sh first."
  exit 1
fi

docker stop osrm_server_ch  2>/dev/null && echo "Stopped existing osrm_server_ch container."  || true
docker stop osrm_server_mld 2>/dev/null && echo "Stopped existing osrm_server_mld container." || true

echo "Starting OSRM CH server (port 5000) ..."
CH_START_MS=$(date +%s%3N)
docker run -d --rm \
  -p 5000:5000 \
  --name osrm_server_ch \
  -v "$DATA_DIR:/data" \
  "$IMAGE" \
  osrm-routed --algorithm ch /data/$OSRM_BASE

PROBE_CH="http://localhost:5000/route/v1/driving/-118.2437,34.0522;-74.006,40.7128?overview=false"
echo "Waiting for CH server to be ready ..."
until curl -sf "$PROBE_CH" > /dev/null 2>&1; do
  sleep 1
done
CH_STARTUP_MS=$(( $(date +%s%3N) - CH_START_MS ))
echo "CH server ready at http://localhost:5000 (${CH_STARTUP_MS} ms)"

echo ""
echo "Starting OSRM MLD server (port 5001) ..."
MLD_START_MS=$(date +%s%3N)
docker run -d --rm \
  -p 5001:5000 \
  --name osrm_server_mld \
  -v "$DATA_DIR:/data" \
  "$IMAGE" \
  osrm-routed --algorithm mld /data/$OSRM_BASE

PROBE_MLD="http://localhost:5001/route/v1/driving/-118.2437,34.0522;-74.006,40.7128?overview=false"
echo "Waiting for MLD server to be ready ..."
until curl -sf "$PROBE_MLD" > /dev/null 2>&1; do
  sleep 1
done
MLD_STARTUP_MS=$(( $(date +%s%3N) - MLD_START_MS ))
echo "MLD server ready at http://localhost:5001 (${MLD_STARTUP_MS} ms)"

# TIMING_FILE="$(pwd)/outputs/osrm_start_timing.json"
# printf '{\n  "ch_startup": %d,\n  "mld_startup": %d\n}\n' \
#   "$CH_STARTUP_MS" "$MLD_STARTUP_MS" > "$TIMING_FILE"
# echo ""
# echo "Startup timings written to $TIMING_FILE"
# echo "To stop: docker stop osrm_server_ch osrm_server_mld"
