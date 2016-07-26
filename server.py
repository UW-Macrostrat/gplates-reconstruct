from flask import Flask, request, jsonify
from reconstruct import reconstruct
from shapely.geometry import mapping
import ast
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def default():
    if request.method == 'POST':
        print type(request.form['shape'])
        print ast.literal_eval(request.form['shape'])
        reconstructed = reconstruct(ast.literal_eval(request.form['shape']), request.form.get('age', type=int))
        return jsonify(**reconstructed)
    else:
        if not request.args.get('lat') or not request.args.get('lng') or not request.args.get('age'):
            return jsonify(**{'error': 'A lng, lat, and age are required'})

        reconstructed = reconstruct({'type': 'Point', 'coordinates': [float(request.args.get('lng')), float(request.args.get('lat'))]}, int(request.args.get('age')))

        return jsonify(**reconstructed)


if __name__ == '__main__':
    app.run()
