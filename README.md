#Get Green Score
The code provided here will be modified to work for you but should give you a clear idea how the scores were calculated.

The green score was calculated by getting the distance from proptery lat/lon coordinates to green spaces in an Open Street Map shapefile.
The calculations were completed using PostGIS extension to a PostgreSQL database.

The shape file can be found in the shpefile directory and was originally downloaded from https://export.hotosm.org/en/v3/

To upload the shapefile into a database named dubuque_shap, the following command was used:
```bash
shp2pgsql -D -I -s 4326 PATH/to/shapefile/DuBuque_planet_osm_polygon_polygons.shp dubuque_shape | psql -d debuque -U <USERNAME>
```

The lat/lon coordinates were determined from the addresses for each property and stored into a table called dubuque_lat_lon. See get_lat_lon.py.

The sql script, get_green_score.sql, is where the green space scores are actually calculated.


