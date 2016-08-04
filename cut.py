from shapely.geometry import shape, MultiPolygon, Polygon, LineString, MultiLineString, Point
import fiona
from rtree import index

# Spatially index the Seton plate set
# Create the spatial index
idx_seton = index.Index()

# Create a hash that can be used to look up a plate_id given a plate index
plate_lookup_seton = {}
plates_seton = []

# Load the plates from a shapefile and spatially index
for pos, plate in enumerate(fiona.open('./StaticPolygons/Shapefile/Seton_etal_ESR2012_StaticPolygons_2012.1.shp')):
    plate_lookup_seton[pos] = plate['properties']['PLATEID1']
    plate_lookup_seton[pos] = {
        'plateid': plate['properties']['PLATEID1'],
        'fromage': plate['properties']['FROMAGE']
    }
    converted = shape(plate['geometry'])
    idx_seton.insert(pos, converted.bounds)
    plates_seton.append(converted)


# Spatially index the EarthByte plate set
# Create the spatial index
idx_eb = index.Index()

# Create a hash that can be used to look up a plate_id given a plate index
plate_lookup_eb = {}
plates_eb = []

# Load the plates from a shapefile and spatially index
for pos, plate in enumerate(fiona.open('./Phanerozoic_EarthByte_ContinentalRegions/reconstructed.shp')):
    plate_lookup_eb[pos] =  {
        'plateid': plate['properties']['PLATEID1'],
        'fromage': plate['properties']['FROMAGE']
    }
    converted = shape(plate['geometry'])
    idx_eb.insert(pos, converted.bounds)
    plates_eb.append(converted)


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

def get_intersecting_plates(bounds, age):
    # Use Seton plates (include seafloor) if < 200 MA
    if age <= 200:
        return [{'geometry': plates_seton[pos], 'plate_id': plate_lookup_seton[pos]['plateid']} for pos in idx_seton.intersection(bounds) if plate_lookup_seton[pos]['fromage'] > age]

    # Use Earthbyte plates (exclude seafloor) if > 200MA
    else:
        return [{'geometry': plates_eb[pos], 'plate_id': plate_lookup_eb[pos]['plateid']} for pos in idx_eb.intersection(bounds) if plate_lookup_eb[pos]['fromage'] > age]

def cut_feature(feature, age):
    pieces = []

    # Use the spatial index (Luke) to get a list of plates this Feature intersects
    intersecting_plates = get_intersecting_plates(feature.bounds, age)

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


def cut(geom, age):
# Accepts a geometry
# Outputs array of objects with a geometry and plate_id
    return cut_feature(geom, age)
