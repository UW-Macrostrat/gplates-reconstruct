from shapely.geometry import shape
from copy import deepcopy
import fiona
from rtree import index
import json
import sys

sys.path.insert(1, './pygplates_rev12_python27_MacOS64')
import pygplates

# Index the available models
models = {}
models_meta = {}

with open('models.json') as in_models:
    plate_models = json.load(in_models)

    for model in plate_models:
        models_meta[model['name']] = deepcopy(model)
        del models_meta[model['name']]['models']

        models[model['name']] = {}

        # Initialize a spatial index for each model
        models[model['name']]['spatial_index'] = index.Index()
        models[model['name']]['plate_lookup'] = {}
        models[model['name']]['plates'] = []
        models[model['name']]['min_age'] = model['min_age']
        models[model['name']]['max_age'] = model['max_age']

        models[model['name']]['models'] = model['models']

        for i, each in enumerate(models[model['name']]['models']):
            file_path = './rotation_models/' + model['name'] + '/' + each['rotation_file']
            models[model['name']]['models'][i]['rotation'] = pygplates.RotationModel(str(file_path))

        # Load and spatially index the plates for each model
        for pos, plate in enumerate(fiona.open('./rotation_models/' + model['name'] + '/plates/plates.shp')):
            # Create a hash that can be used to look up a plate_id given a plate index
            models[model['name']]['plate_lookup'][pos] = {
                'plateid': plate['properties']['PLATEID1'],
                'fromage': plate['properties']['FROMAGE']
            }
            converted = shape(plate['geometry'])
            # Add to the spatial index
            models[model['name']]['spatial_index'].insert(pos, converted.bounds)
            models[model['name']]['plates'].append(converted)
