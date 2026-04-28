import time
import requests
from pamda import pamda

OSRM_CH_HOST  = "http://localhost:5000"
OSRM_MLD_HOST = "http://localhost:5001"

# Same cities and pairing logic as geo_time_comparison_tests.py
cities = {
    'Los Angeles':     (34.0522,  -118.2437),
    'New York City':   (40.7128,   -74.0060),
    'Chicago':         (41.8781,   -87.6298),
    'Houston':         (29.7604,   -95.3698),
    'Phoenix':         (33.4484,  -112.0740),
    'Denver':          (39.7392,  -104.9903),
    'Seattle':         (47.6062,  -122.3321),
    'Miami':           (25.7617,   -80.1918),
    'Washington D.C.': (38.9072,   -77.0369),
    'San Francisco':   (37.7749,  -122.4194),
    'Omaha':           (41.2565,   -95.9345),
    'Atlanta':         (33.7490,   -84.3880),
    'Austin':          (30.2672,   -97.7431),
    'Boston':          (42.3601,   -71.0589),
    'Las Vegas':       (36.1699,  -115.1398),
    'Detroit':         (42.3314,   -83.0458),
}


def test_osrm(coord1, coord2, host):
    # OSRM expects longitude,latitude order (GeoJSON convention)
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    url = f"{host}/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if data.get('code') != 'Ok':
        return None
    return data['routes'][0]['distance'] / 1000  # meters → km


def test_osrm_ch(coord1, coord2):
    return test_osrm(coord1, coord2, OSRM_CH_HOST)


def test_osrm_mld(coord1, coord2):
    return test_osrm(coord1, coord2, OSRM_MLD_HOST)


def wait_for_server(host, label):
    lat1, lon1 = cities['Los Angeles']
    lat2, lon2 = cities['New York City']
    url = f"{host}/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
    print(f"Checking OSRM {label} server availability ...")
    for attempt in range(30):
        try:
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                print(f"  {label} server is ready.")
                return
        except requests.exceptions.ConnectionError:
            pass
        print(f"  Not ready yet, retrying ({attempt + 1}/30) ...")
        time.sleep(2)
    raise RuntimeError(
        f"OSRM {label} server not reachable at {host}. "
        "Run ./osrm_setup.sh first."
    )


setup_timing = pamda.read_json('outputs/osrm_setup_timing.json')
wait_for_server(OSRM_CH_HOST,  'CH')
wait_for_server(OSRM_MLD_HOST, 'MLD')

output = []
cities_fully_visited = []

print("\nQuerying OSRM for each city pair ...")
for city1, coord1 in cities.items():
    print(f"  From {city1} ...")
    for city2, coord2 in cities.items():
        if city1 != city2 and city2 not in cities_fully_visited:
            t0 = time.perf_counter()
            ch_length = test_osrm_ch(coord1, coord2)
            ch_elapsed_ms = (time.perf_counter() - t0) * 1000

            t0 = time.perf_counter()
            mld_length = test_osrm_mld(coord1, coord2)
            mld_elapsed_ms = (time.perf_counter() - t0) * 1000

            output.append({
                'city1': city1,
                'city2': city2,
                'coord1': coord1,
                'coord2': coord2,
                'test_osrm_ch_time_ms':   ch_elapsed_ms,
                'test_osrm_ch_length_km': ch_length,
                'test_osrm_mld_time_ms':   mld_elapsed_ms,
                'test_osrm_mld_length_km': mld_length,
                # One-time setup costs — same value on every row so the CSV
                # is self-contained and can be analysed independently.
                'osrm_pull_ms':        setup_timing['pull_ms'],
                'osrm_download_ms':    setup_timing['download_ms'],
                'osrm_extract_ms':     setup_timing['extract_ms'],
                'osrm_contract_ms':    setup_timing['contract_ms'],
                'osrm_partition_ms':   setup_timing['partition_ms'],
                'osrm_customize_ms':   setup_timing['customize_ms'],
                'osrm_ch_startup_ms':  setup_timing['ch_startup_ms'],
                'osrm_mld_startup_ms': setup_timing['mld_startup_ms'],
            })

    cities_fully_visited.append(city1)

pamda.write_csv(data=output, filename='outputs/osrm_time_tests.csv')
print(f"\nWrote {len(output)} rows to outputs/osrm_time_tests.csv")
