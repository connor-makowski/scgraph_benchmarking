
from scgraph.geographs.marnet import marnet_geograph
from scgraph.geographs.us_freeway import us_freeway_geograph
from scgraph.geographs.north_america_rail import north_america_rail_geograph
from scgraph.geographs.oak_ridge_maritime import oak_ridge_maritime_geograph
from scgraph_data.world_highways import world_highways_geograph
from scgraph_data.world_highways_and_marnet import world_highways_and_marnet_geograph
from scgraph_data.world_railways import world_railways_geograph

for name, scgraph_object in [
    ('Marnet', marnet_geograph),
    ('US Freeway', us_freeway_geograph),
    ('North America Rail', north_america_rail_geograph),
    ('Oak Ridge Maritime', oak_ridge_maritime_geograph),
    ('World Highways', world_highways_geograph),
    ('World Highways and Marnet', world_highways_and_marnet_geograph),
    ('World Railways', world_railways_geograph)
]:
    scgraph_object.save_as_geojson(f"geojsons/{name.lower().replace(' ', '_')}.geojson", compact=True)