# GPlates reconstruction service
A simple web interface for interacting with the `pygplates` library.

### Info
##### Rotation model
If the input age is less than or equal to 200 MA, the following rotation model is used:

````
Seton, M., Müller, R.D., Zahirovic, S., Gaina, C., Torsvik, T., G., S., Talsma, A., Gurnis, M., Turner, M., Maus, S., Chandler, M., 2012, Global continental and ocean basin reconstructions since 200 Ma, Earth Science Reviews, 113: 212-270
````
It can be found [here](ftp://earthbyte.org/earthbyte/GPlates/SampleData_GPlates1.5/Individual/FeatureCollections/Rotations.zip).

If the input age is greater than 200 MA, the following rotation model is used:

````
Wright, N., S. Zahirovic, R. D. Müller, and M. Seton (2013), Towards community-driven, open-access paleogeographic reconstructions: integrating open-access paleogeographic and paleobiology data with plate tectonics, Biogeosciences, 10, 1529-1541
````
It can be found [here](ftp://ftp.earthbyte.org/papers/Wright_etal_Paleobiogeography/1_Phanerozoic_Plate_Motions_GPlates.zip)


##### Plates
The geometry used to assign plate IDs is from Seton et. al and can be found [here](ftp://earthbyte.org/earthbyte/GPlates/SampleData_GPlates1.5/Individual/FeatureCollections/StaticPolygons.zip).

### Oddities
+ Because of an oddity with pygplates, `null` property values in the input are converted to empty strings in the output.
+ In order to preserve original geometry types, polygons that span multiple plates are divided into multiple features, one for each plate. Thus if one polygon is provided and it sits on three plates, three features will be returned, one for each plate.


## Usage

### via GET request
Because there is a max length for URLs, only simple point queries are available with a GET request.

#### Example
Reconstruct a point to 100 MA
````
curl -o point100.geojson https://dev.macrostrat.org/reconstruct?lng=-89&lat=43&age=100
````

#### Required parameters
+ **lng** - a valid longitude (WGS84)
+ **lat** - a valid latitude (WGS84)
+ **age** - the target reconstruction time in millions of years before present. Can be any integer between 0 and 550

#### Output
Returns a GeoJSON FeatureCollection. There will be one Feature, the input point, and it will have a property `plate_id` indicating which plate the point was assigned to.

### via POST request

#### Example
Reconstruct a polygon to 100 MA
````
curl -X POST -F 'shape={"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[-103.71093749999999,37.43997405227057],[-103.71093749999999,46.07323062540835],[-84.0234375,46.07323062540835],[-84.0234375,37.43997405227057],[-103.71093749999999,37.43997405227057]]]}}' -F 'age=100' -o polygon100.geojson https://dev.macrostrat.org/reconstruct
````
#### Required parameters
+ **shape** - a valid GeoJSON object
+ **age** - the target reconstruction time. Can be any integer between 0 and 550

#### Output
Returns a GeoJSON FeatureCollection. Each Feature will have a property `plate_id` indicating which plate the feature was assigned to.
