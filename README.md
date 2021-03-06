# GPlates reconstruction service
A simple web interface for interacting with the `pygplates` python library. For more information see [pygplates documentation](http://www.gplates.org/docs/pygplates/). 

### Info
##### Rotation model
The following rotation model is used:

````
Wright, N., S. Zahirovic, R. D. Müller, and M. Seton (2013), Towards
  community-driven, open-access paleogeographic reconstructions:
  integrating open-access paleogeographic and paleobiology data with
  plate tectonics, Biogeosciences, 10, 1529-1541
````
<!---
ftp://ftp.earthbyte.org/papers/Wright_etal_Paleobiogeography/1_Phanerozoic_Plate_Motions_GPlates.zip
--->

It can be found [here](http://tinyurl.com/jm2s3av).


##### Plates
<!---
ftp://earthbyte.org/earthbyte/GPlates/SampleData_GPlates1.5/Individual/FeatureCollections/StaticPolygons.zip
--->
The geometry used to assign plate IDs is from Seton et. al (2012) and can be found [here](http://tinyurl.com/hxj366w).

### Oddities
+ Because of an oddity with pygplates, `null` property values in the input are converted to empty strings in the output.
+ In order to preserve original geometry types, polygons that span multiple plates are divided into multiple features, one for each plate. Thus if one polygon is provided and it sits on three plates, three features will be returned, one for each plate.
+ Plates have a valid age range. Thus if a point is assigned to a plate with a valid age of 0-20MA, and it is reconstructed to 15 MA, a valid geometry will be returned. However, if it is reconstructed to 21 MA, a `null` geometry will be returned along with a `null` plateid.
+ If a polygon argument is not entirely contained by a plate, then the polygon argument is divided between the areas of the plates that it does intersect. If all intersecting portions of the polygon can be rotated to the specified age, then the rotations will occur independently for each segment of the original polygon. If one or more of the plates intersecting the polygon do not have rotations for the specified age, NULL values for that plate segment will be returned.

## Usage

### single point via GET request
If you have a single point to reconstruct, you can use a simple GET request.

#### Example
Reconstruct a point to 100 MA
````
curl -o point100.geojson 'https://macrostrat.org/gplates/reconstruct?lng=-89&lat=43&age=100'
````

#### Required parameters
+ **lng** - a valid longitude (WGS84)
+ **lat** - a valid latitude (WGS84)
+ **age** - the target reconstruction time in millions of years before present. Can be any integer between 0 and 550.

#### Output
Returns a GeoJSON FeatureCollection. There will be one Feature, the input point, and it will have a property `plate_id` indicating which plate the point was assigned to.

### list of points via GET request
You can also reconstruct a list of points via a GET request.  Because there is a maximum length on a URL, don't make the list overly long.

#### Example
Reconstruct a list of points to 100 MA
````
curl -o point100.geojson 'https://macrostrat.org/gplates/reconstruct?points=-89,43,1%20-92.5,43.2,2&age=100'
````

#### Required parameters
+ **points** - a list of points, separated by whitespace.  Each point must consist of a longitude and latitude, separated by a comma.  You may also append a label to each point, also separated by a comma.
+ **age** - the target reconstruction time in millions of years before present.  Can be any integer between 0 and 550.

#### Output
Returns a list of GeoJSON FeatureCollections, one for each input point.  Each will contain one Feature.  This Feature will have a property `plate_id` indicating which plate the point was assigned to.  For every point for which a label was specified, the resulting feature will have a property `label` whose value is the specified label.

### via POST request

#### Example
Reconstruct a polygon to 100 MA
````
curl -X POST -F \
'shape={"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[-103.71093749999999,37.43997405227057],[-103.71093749999999,46.07323062540835],[-84.0234375,46.07323062540835],[-84.0234375,37.43997405227057],[-103.71093749999999,37.43997405227057]]]}}' \
-F 'age=100' -o polygon100.geojson \
https://macrostrat.org/gplates/reconstruct
````

Reconstruct an entire file:
````
curl -X POST -F "shape=$(cat myfile.geojson)" \
-F 'age=69' -o reconstructed_myfile.geojson \
https://macrostrat.org/gplates/reconstruct
````
#### Required parameters
+ **shape** - a valid GeoJSON object
+ **age** - the target reconstruction time. Can be any integer between 0 and 550

#### Output
Returns a GeoJSON FeatureCollection. Each Feature will have a property `plate_id` indicating which plate the feature was assigned to.
