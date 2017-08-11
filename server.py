from flask import Flask, request, jsonify, make_response, current_app
from datetime import timedelta
from reconstruct import reconstruct
from shapely.geometry import mapping
import ast
import json
from functools import update_wrapper

import json

from models import models_meta, models

with open('models.json') as in_models:
    plate_models = json.load(in_models)
    for model in plate_models:
        del model['models']

app = Flask(__name__)

# Make sure response is properly encoded
app.config['JSON_AS_ASCII'] = False

def validate_params(age, model):
    if not model in models_meta:
        return 'Invalid model. Please choose a valid model from /models'

    if age < models_meta[model]['min_age']:
        return 'The minimum age of this model is %s.' % (models_meta[model]['min_age'], )

    if age > models_meta[model]['max_age']:
        return 'The maximum age of this model is %s.' % (models_meta[model]['max_age'], )

    return False

# Factory for returning errors to the client
def throw_error(msg, code=400):
    resp = make_response('{"error": "' + msg + '"}\n', code)
    resp.headers['Content-Type'] = 'application/json'
    return resp


def crossdomain(origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True, automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


@app.route('/gplates/reconstruct', methods=['GET', 'POST'])
@crossdomain(origin='*')
def default(send_wildcard=True):
    if request.method == 'POST':
        if 'shape' not in request.form or 'age' not in request.form:
            return throw_error('A shape and age parameter are required when POSTing.')

        reconstructed = reconstruct(json.loads(request.form['shape']), request.form.get('age', type=int))
        return jsonify(**reconstructed)

    elif request.args.get('points'):
        if not request.args.get('age'):
            return throw_error('You must specify an age parameter that is approriate for the given model')

        points = request.args.get('points').split()
        age = int(request.args.get('age'))
        result = [ ]
        for p in points:
            coords = p.split(',')
            reconstructed = reconstruct({'type': 'Point', 'coordinates': [float(coords[0]), float(coords[1])]}, age)
            if len(coords) > 2:
                reconstructed['features'][0]['properties']['label'] = coords[2]
            result.append(reconstructed)
        if request.args.get('format') and request.args.get('format') == 'geojson_bare':
            return jsonify(**{'type': 'FeatureCollection', 'features': [ item for r in [feature for feature in [ fc['features'] for fc in result ]] for item in r ]})
        else:
            return jsonify(**{'result': result})

    else:
        if not request.args.get('lat') or not request.args.get('lng') or not request.args.get('age'):
            return throw_error('A lng, lat, and age are required. See documentation at https://github.com/UW-Macrostrat/gplates-reconstruct')

        model = request.args.get('model')
        age = int(request.args.get('age'))

        validation_error = validate_params(age, model)
        if validation_error:
            return throw_error(validation_error)

        reconstructed = reconstruct({'type': 'Point', 'coordinates': [float(request.args.get('lng')), float(request.args.get('lat'))]}, age, model)

        return jsonify(**reconstructed)


@app.route('/gplates/models', methods=['GET'])
@crossdomain(origin='*')
def models(send_wildcard=True):
    return jsonify(plate_models)


if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5050)
