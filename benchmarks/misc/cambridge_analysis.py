import csv
import statistics

def calculate_r_squared(y_true, y_pred):
    y_true_mean = sum(y_true) / len(y_true)
    sst = sum([(y - y_true_mean)**2 for y in y_true])
    ssr = sum([(y_true[i] - y_pred[i])**2 for i in range(len(y_true))])
    if sst == 0: return 1.0 if ssr == 0 else float('-inf')
    return 1 - (ssr / sst)

def mape(y_true, y_pred):
    return sum([abs(yt - yp) / yt for yt, yp in zip(y_true, y_pred)]) / len(y_true) * 100

data = []
with open('outputs/cambridge_osmnx_scgraph_comparison.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        data.append({k: float(v) if k not in ('origin', 'destination') else v for k, v in row.items()})

print("Average Solve Times (ms):")
for key in ['scgraph_time_optimized', 'osmnx_time_optimized', 'scgraph_distance_optimized', 'osmnx_distance_optimized', 'google']:
    durations = [r[f'{key}_duration_seconds'] * 1000 for r in data]
    print(f"{key}: {statistics.mean(durations):.2f} +/- {statistics.stdev(durations):.2f}")

print("\nDistance vs Google (km):")
y_true = [r['google_distance_km'] for r in data]
for key in ['scgraph_time_optimized', 'osmnx_time_optimized', 'scgraph_distance_optimized', 'osmnx_distance_optimized']:
    y_pred = [r[f'{key}_distance_km'] for r in data]
    print(f"{key} -> R^2: {calculate_r_squared(y_true, y_pred):.4f}, MAPE: {mape(y_true, y_pred):.2f}%")

print("\nTravel Time vs Google (seconds):")
y_true = [r['google_time_seconds'] for r in data]
for key in ['scgraph_time_optimized', 'osmnx_time_optimized', 'scgraph_distance_optimized', 'osmnx_distance_optimized']:
    y_pred = [r[f'{key}_time_seconds'] for r in data]
    print(f"{key} -> R^2: {calculate_r_squared(y_true, y_pred):.4f}, MAPE: {mape(y_true, y_pred):.2f}%")

