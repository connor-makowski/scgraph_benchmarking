from scgraph import GeoGraph

marnet_geograph = GeoGraph.load_geograph('marnet')
us_freeway_geograph = GeoGraph.load_geograph('us_freeway')
north_america_rail_geograph = GeoGraph.load_geograph('north_america_rail')
oak_ridge_maritime_geograph = GeoGraph.load_geograph('oak_ridge_maritime')
world_highways_geograph = GeoGraph.load_geograph('world_highways')
world_highways_and_marnet_geograph = GeoGraph.load_geograph('world_highways_and_marnet')
world_railways_geograph = GeoGraph.load_geograph('world_railways')

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