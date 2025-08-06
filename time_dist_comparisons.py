from pamda.pamda_timer import pamda_timer
from pamda import pamda

from utils.solvers import (
    test_google,
    test_world_highways_scgraph,
    test_us_freeway_scgraph,
    test_osmnx,
)

# Los Angeles to San Diego
LA = (34.0522, -118.2437)
SD = (32.7157, -117.1611)

# Orlando to Tampa
ORL = (28.5383, -81.3792)
TAM = (27.9506, -82.4572)

# New York City to Philadelphia
NYC = (40.7128, -74.0060)
PHI = (39.9526, -75.1652)

wh = pamda_timer(test_world_highways_scgraph, iterations=10)
uf = pamda_timer(test_us_freeway_scgraph, iterations=10)
ox = pamda_timer(test_osmnx, iterations=10)
go = pamda_timer(test_google, iterations=10)


output = []
for function in (wh, uf, ox, go):
    for combination in [("LA_SD", LA, SD), ("ORL_TAM", ORL, TAM), ("NYC_PHI", NYC, PHI)]:
        output_item = function.get_time_stats(combination[1], combination[2])
        output_item['combination'] = combination[0]
        output_dist = function(combination[1], combination[2])
        output_item['distance_km'] = output_dist
        output.append(output_item)
        

pamda.write_csv(data=output, filename='outputs/time_dist_comparisons.csv')