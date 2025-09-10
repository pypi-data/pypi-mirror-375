import geoformat


# metadata_field_int
# metadata_field_float
# metadata_field_

point_geometry = {"type": "Point", "coordinates": [-115.81, 37.24]}
linestring_geometry = {
    "type": "LineString",
    "coordinates": [[8.919, 44.4074], [8.923, 44.4075]],
}
polygon_geometry = {
    "type": "Polygon",
    "coordinates": [
        [[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]],
        [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]],
    ],
}
multipoint_geometry = {
    "type": "MultiPoint",
    "coordinates": [[-155.52, 19.61], [-156.22, 20.74], [-157.97, 21.46]],
}
multilinestring_geometry = {
    "type": "MultiLineString",
    "coordinates": [
        [[3.75, 9.25], [-130.95, 1.52]],
        [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]],
    ],
}
multipolygon_geometry = {
    "type": "MultiPolygon",
    "coordinates": [
        [[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]],
        [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]],
    ],
}
geometrycollection_geometry = {
    "type": "GeometryCollection",
    "geometries": [
        {"type": "Point", "coordinates": [-115.81, 37.24]},
        {"type": "LineString", "coordinates": [[8.919, 44.4074], [8.923, 44.4075]]},
        {
            "type": "Polygon",
            "coordinates": [
                [[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]],
                [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]],
            ],
        },
        {
            "type": "MultiPoint",
            "coordinates": [[-155.52, 19.61], [-156.22, 20.74], [-157.97, 21.46]],
        },
        {
            "type": "MultiLineString",
            "coordinates": [
                [[3.75, 9.25], [-130.95, 1.52]],
                [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]],
            ],
        },
        {
            "type": "MultiPolygon",
            "coordinates": [
                [[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]],
                [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]],
            ],
        },
    ],
}

# ESRI SHAPEFILE
#
#   ATTRIBUTES
#       fields :
#           field name: LEN FIELD NAME < 10
#
#               field type: required ONLY
#               field width: required max 255
#               field precsion: required if float
#
#
#   GEOMETRY
#       - strict separation
#           - Geometry
#           - No Geometry
#           - Point
#           - Linestring | MultliLinestring
#           - Polygon | Multipolygon
#           - MultiPoint
#       [[0],[1], [2, 5], [3, 6], [4], [100]]
