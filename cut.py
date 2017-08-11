from shapely.geometry import shape, MultiPolygon, Polygon, LineString, MultiLineString, Point
from models import models


def handleMultiLineString(geometry):
    if (len(geometry.geoms) == 0):
        return []
    else:
        return [geom for geom in geometry.geoms if geom.geom_type == 'LineString']

def handleMultiPolygon(geometry):
    if (len(geometry.geoms) == 0):
        return []
    else:
        return [geom for geom in geometry.geoms if geom.geom_type == 'Polygon']

def handleGeometryCollection(geometry):
    if (len(geometry.geoms) == 0):
        return []
    else:
        print 'Non-empty geometry collection'
        return []

def get_intersecting_plates(bounds, model):
    # Use Earthbyte plates (exclude seafloor)

    return [{'geometry': models[model]['plates'][pos], 'plate_id': models[model]['plate_lookup'][pos]['plateid']} for pos in models[model]['spatial_index'].intersection(bounds)]

# Accepts a geometry
# Outputs array of objects with a geometry and plate_id
def cut(feature, age, model):
    pieces = []

    # Use the spatial index (Luke) to get a list of plates this Feature intersects
    intersecting_plates = get_intersecting_plates(feature.bounds, model)

    # For each intersecting plate, get the intersection with the target Feature
    for plate in intersecting_plates:
        chunk = plate['geometry'].intersection(feature)

        # If chunk is iterable, it is multigeom
        try:
            chunk = [ { 'geometry': c, 'plate_id': plate['plate_id'] } for c in chunk.geoms ]
        except:
            chunk = [ { 'geometry': chunk, 'plate_id': plate['plate_id'] }]


        if isinstance(chunk, list):
            exploded = chunk
        else:
            exploded = []

        if len(exploded) > 0:
            pieces = pieces + exploded

    # If the feature doesn't intersect any plates, return a null geometry
    if len(pieces) == 0:
        pieces = [ { 'geometry': None, 'plate_id': None } ]

    return pieces
