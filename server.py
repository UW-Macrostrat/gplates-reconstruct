from flask import Flask, request, jsonify, make_response
from reconstruct import reconstruct
from shapely.geometry import mapping
import ast
import json
app = Flask(__name__)

@app.route('/reconstruct', methods=['GET', 'POST'])
def default():
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
