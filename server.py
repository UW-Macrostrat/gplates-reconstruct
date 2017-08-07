from flask import Flask, request, jsonify, make_response, current_app
from datetime import timedelta  
from reconstruct import reconstruct
from shapely.geometry import mapping
import ast
import json
from functools import update_wrapper
app = Flask(__name__)

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


@app.route('/reconstruct', methods=['GET', 'POST'])
@crossdomain(origin='*')
def default(send_wildcard=True):
    if request.method == 'POST':
        if 'shape' not in request.form or 'age' not in request.form:
            resp = make_response('{"error": "A shape and age are required. See documentation at https://github.com/UW-Macrostrat/gplates-reconstruct"}\n', 400)
            resp.headers['Content-Type'] = 'application/json'
            return resp

        reconstructed = reconstruct(json.loads(request.form['shape']), request.form.get('age', type=int))
        return jsonify(**reconstructed)
    elif request.args.get('points'):
        if not request.args.get('age'):
            resp = make_response('{"error": "You must specify an age. See documentation at https://github.com/UW-Macrostrat/gplates-reconstruct"}\n', 400)
            resp.headers['Content-Type'] = 'application/json'
            return resp
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
            resp = make_response('{"error": "A lng, lat, and age are required. See documentation at https://github.com/UW-Macrostrat/gplates-reconstruct"}\n', 400)
            resp.headers['Content-Type'] = 'application/json'
            return resp
        reconstructed = reconstruct({'type': 'Point', 'coordinates': [float(request.args.get('lng')), float(request.args.get('lat'))]}, int(request.args.get('age')))

        return jsonify(**reconstructed)


if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5050)
