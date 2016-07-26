from shapely.geometry import shape, MultiPolygon, Polygon, LineString, MultiLineString, Point
import fiona
from rtree import index

# Create the spatial index
idx = index.Index()

# Create a hash that can be used to look up a plate_id given a plate index
plate_lookup = {}
plates = []

# Load the plates from a shapefile and spatially index
for pos, plate in enumerate(fiona.open('./StaticPolygons/shapefile/Seton_etal_ESR2012_StaticPolygons_2012.1.shp')):
    plate_lookup[pos] = plate['properties']['PLATEID1']
    converted = shape(plate['geometry'])
    idx.insert(pos, converted.bounds)
    plates.append(converted)

geom_types = {
    'Polygon': Polygon,
    'LineString': LineString,
    'Point': Point
}

multi_geom_types = {
    'Polygon': MultiPolygon,
    'LineString': MultiLineString
}


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



def get_intersecting_plates(bounds):
    return [{'geometry': plates[pos], 'plate_id': plate_lookup[pos]} for pos in idx.intersection(bounds)]


def cut_feature(feature):
    pieces = []

    # Use the spatial index (Luke) to get a list of plates this Feature intersects
    intersecting_plates = get_intersecting_plates(feature.bounds)

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

    return pieces


def handle_output_separate(feature, pieces):
    if len(pieces) == 1:
        return [ {'properties': feature['properties'], 'geometry' : geom_types[pieces[0]['geometry'].geom_type](pieces[0]['geometry']) } ]
    elif len(pieces) > 1:
        return [ {'properties': feature['properties'], 'geometry' : geom_types[piece['geometry'].geom_type](piece['geometry']) } for piece in pieces ]
    else:
        return []


def cut(geom):
# Accepts a geometry
# Outputs array of objects with a geometry and plate_id
    return cut_feature(geom)
