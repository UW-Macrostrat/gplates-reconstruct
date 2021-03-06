'''
Interface for pygplates reconstruction method
Public methods:
@reconstruct([geojson], [age], ?[model])

+ Splits items on to plates and rotates them to the desired age
+ Because of oddities with pygplates, it also converts properties
  to UTF-8 and replaces null values with empty strings
+ Adds a property value 'plate_id' to each feature as well

'''
from cut import cut
import json
from datetime import datetime
from copy import deepcopy
import time
from shapely.geometry import mapping, shape, MultiPolygon, Polygon, LineString, MultiLineString, Point

import sys
sys.path.insert(1, './pygplates_rev12_python27_MacOS64')
import pygplates

from models import models, models_meta

# *sigh....* pygplates requires props to be UTF-8 encoded and not contain any null values...
def encode_props(props):
    encoded = {}
    for key, value in props.items():
        if isinstance(value, basestring):
            encoded[key.encode('utf8')] = value.encode('utf8')
        elif value is None:
            encoded[key.encode('utf8')] = ''
        else:
            encoded[key.encode('utf8')] = value

    return encoded

def construct_gplate_feature(f, plateid, props):
    gplateFeature = pygplates.Feature(pygplates.FeatureType.gpml_unclassified_feature)
    gplateFeature.set_reconstruction_plate_id(int(plateid))

    # Once reconstructed we can't retrieve the geometry type, so record it now as a description
    # This allows us to correctly form GeoJSON later
    gplateFeature.set_description(f.geom_type)

    # Record all properties
    if props:
        gplateFeature.set_shapefile_attributes(encode_props(props))

    if f.geom_type == 'Point':
        gplateFeature.set_geometry(pygplates.PointOnSphere((f.coords[0][1], f.coords[0][0], )))
    elif f.geom_type == 'MultiPoint':
        gplateFeature.set_geometry(pygplates.MultiPointOnSphere([ pygplates.PointOnSphere((each[1], each[0], )) for each in f ]))
    elif f.geom_type == 'LineString':
        gplateFeature.set_geometry(pygplates.PolylineOnSphere([ pygplates.PointOnSphere((each[1], each[0], )) for each in f.coords ]))
    elif f.geom_type == 'Polygon':
        gplateFeature.set_geometry(pygplates.PolygonOnSphere([ pygplates.PointOnSphere((each[1], each[0], )) for each in f.exterior.coords ]))
    else:
        print 'huh?'

    return gplateFeature


def rotate(features, age, model):
    if len(models[model]['models']) == 1:
        rotation_model = models[model]['models'][0]['rotation']

    for rot in models[model]['models']:
        if rot['min_age'] <= age and rot['max_age'] >= age:
            rotation_model = rot['rotation']

    rotated = []
    pygplates.reconstruct(features, rotation_model, rotated, age)
    return rotated


def build_geojson(gtype, coords):
    geojson = {'type': gtype, 'coordinates': []}
    if gtype == 'Polygon':
        geojson['coordinates'] = [[ [coord[1], coord[0]] for coord in coords ]]
    elif gtype == 'Point':
        geojson['coordinates'] = [coords[0][1], coords[0][0]]
    elif gtype == 'LineString':
        geojson['coordinates'] = [ [coord[1], coord[0]] for coord in coords ]

    return geojson


def geojsonify(features):
    return [{ 'geometry':  shape(build_geojson(each.get_feature().get_description(), each.get_reconstructed_geometry().to_lat_lon_array())), 'properties': each.get_feature().get_shapefile_attributes() } for each in features]

def reconstruct_feature(props, f, age, model):
    model = model or 'write2013'

    rotated = []
    cut_feature = cut(f, age, model)

    features = []
    not_rotated = []
    for piece in cut_feature:
        new_props = deepcopy(props)
        new_props['plate_id'] = piece['plate_id']
        if piece['plate_id']:
            features.append(construct_gplate_feature(piece['geometry'], piece['plate_id'], new_props))
        else:
            not_rotated.append({
                'type': 'Feature',
                'properties': new_props,
                'geometry': None
            })

    rotated = geojsonify(rotate(features, age, model))
    output = {
        'type': 'FeatureCollection',
        'properties': {
            'model': models_meta[model],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'age': age
        },
        'features': [
            {'type': 'Feature', 'properties': f['properties'], 'geometry': mapping(f['geometry']) } for f in rotated
        ]
    }

    output['features'] = output['features'] + not_rotated

    return output

def reconstruct(input_geojson, age, model='wright2013'):

    if 'features' in input_geojson:
        features = []
        not_rotated = []

        for feature in input_geojson['features']:
            # Returns list of dictionaries with a 'geometry' and 'plate_id'
            cut_feature = cut(shape(feature['geometry']), age)

            for each in cut_feature:
                # The plate_id is recorded as a property so that it can be attached to the output
                new_props = deepcopy(feature['properties'])
                new_props['plate_id'] = each['plate_id']
                if each['plate_id']:
                    features.append(construct_gplate_feature(each['geometry'], each['plate_id'], new_props))
                else:
                    not_rotated.append({
                        'type': 'Feature',
                        'properties': new_props,
                        'geometry': None
                    })


        # Reconstruct the geometries to the given age parse into GeoJSON
        rotated = geojsonify(rotate(features, age, model))

        output = {
            'type': 'FeatureCollection',
            'properties': {
                'model': models_meta[model],
                'date': datetime.now().strftime('%Y-%m-%d'),
                'age': age
            },
            'features': [
                {'type': 'Feature', 'properties': f['properties'], 'geometry': mapping(f['geometry']) } for f in rotated
            ]
        }

        output['features'] = output['features'] + not_rotated

        return output

    else:
        props = input_geojson['properties'] if 'properties' in input_geojson else {}
        geom = shape(input_geojson['geometry']) if 'geometry' in input_geojson else shape(input_geojson)

        return reconstruct_feature(props, geom, age, model)
