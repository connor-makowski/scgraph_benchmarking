import requests
from pamda import pamda
from pamda.pamda_timer import pamda_timer

OSRM_CH_HOST  = "http://localhost:5000"
OSRM_MLD_HOST = "http://localhost:5001"

# Same city pairs as time_dist_comparisons.py
LA  = (34.0522, -118.2437)
SD  = (32.7157, -117.1611)
ORL = (28.5383, -81.3792)
TAM = (27.9506, -82.4572)
NYC = (40.7128, -74.0060)
PHI = (39.9526, -75.1652)

combinations = [
    ("LA_SD",   LA,  SD),
    ("ORL_TAM", ORL, TAM),
    ("NYC_PHI", NYC, PHI),
]


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


def make_setup_row(function_name, elapsed_ms):
    # One-time global cost; not per-combination.
    return {
        'module':      'osrm_setup',
        'function':    function_name,
        'unit':        'ms',
        'iterations':  1,
        'avg':         elapsed_ms,
        'min':         elapsed_ms,
        'max':         elapsed_ms,
        'std':         0,
        'combination': 'global',
        'category':    'setup',
        'solver':      function_name,
        'distance_km': None,
    }


output = []

# ── One-time setup costs (from osrm_setup.sh) ─────────────────────────────────
setup_timing = pamda.read_json('outputs/osrm_setup_timing.json')

for key in ('pull_ms', 'download_ms', 'extract_ms', 'contract_ms',
            'partition_ms', 'customize_ms', 'ch_startup_ms', 'mld_startup_ms'):
    output.append(make_setup_row(
        function_name=f'osrm_{key[:-3]}',  # strip trailing _ms
        elapsed_ms=setup_timing[key],
    ))

# ── Per-combination query timing ──────────────────────────────────────────────
osrm_ch_timer  = pamda_timer(test_osrm_ch,  iterations=10)
osrm_mld_timer = pamda_timer(test_osrm_mld, iterations=10)

print("\n===============")
print("OSRM Time/Distance Comparisons:")
print("===============")

for combo_name, coord1, coord2 in combinations:
    print(f"\n{combo_name}:")

    ch_item = osrm_ch_timer.get_time_stats(coord1, coord2)
    ch_item['module']      = 'osrm_time_dist_comparisons.test_osrm_ch'
    ch_item['combination'] = combo_name
    ch_item['category']    = 'network_solve'
    ch_item['solver']      = 'osrm_ch'
    ch_item['distance_km'] = test_osrm_ch(coord1, coord2)
    output.append(ch_item)

    mld_item = osrm_mld_timer.get_time_stats(coord1, coord2)
    mld_item['module']      = 'osrm_time_dist_comparisons.test_osrm_mld'
    mld_item['combination'] = combo_name
    mld_item['category']    = 'network_solve'
    mld_item['solver']      = 'osrm_mld'
    mld_item['distance_km'] = test_osrm_mld(coord1, coord2)
    output.append(mld_item)

    print(f"  OSRM CH:  {ch_item['avg']:.2f} ms (stdev: {ch_item['std']:.2f}) | {ch_item['distance_km']:.2f} km")
    print(f"  OSRM MLD: {mld_item['avg']:.2f} ms (stdev: {mld_item['std']:.2f}) | {mld_item['distance_km']:.2f} km")

pamda.write_csv(data=output, filename='outputs/osrm_time_dist_comparisons.csv')
print("\nWrote outputs/osrm_time_dist_comparisons.csv")
