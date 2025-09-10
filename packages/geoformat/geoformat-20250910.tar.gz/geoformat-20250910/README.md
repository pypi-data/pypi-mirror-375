# Welcome to Geoformat

## Introduction

Geoformat is a geospatial library.
The library aims to simplify loading data, manipulations, and storage of geospatial data.
Currently, this library is in Alpha mode. This means that at the moment, the structure of this library is not fully object-oriented compatible.

* [Installation](#installation)
* [Geoformat Cookbook](#geoformat-cookbook)
* [Geoformat Technical Description [WIP]](#geoformat-technical-description)
* [Table of Contents](#table-of-contents)



## Installation

``` sh
$ pip install geoformat
```

## Geoformat Cookbook


* [Create geoformat objects](#create-geoformat-objects)
  * [Create a feature](#create-a-feature)
  * [Create a geolayer](#create-a-geolayer)
  * [Print data geolayer](#print-data-geolayer)
  * [Draw a Geometry](#draw-a-geometry)
* [Geometry usefully functions](#geometry-usefully-functions)
  * [Area, length, distance, bbox and centroid](#area-length-distance-bbox-and-centroid)
  * [Reproject](#reproject-)
  * [Geometry formatting](#geometry-formatting)
  * [Geometrics manipulations](#geometrics-manipulations)
  * [Low level geometrics objects](#low-level-geometrics-objects)
  * [Geometry Index and Matrix](#geometry-index-and-matrix)
* [Attributes usefully functions](#attributes-usefully-functions)
  * [Attributes index](#attributes-index)
  * [Join geolayer attributes](#join-geolayer-attributes)
  * [Clause functions](#clause-functions)
  * [Field statistics](#field-statistics)
* [Feature usefully functions](#feature-usefully-functions)
* [Geolayer usefully functions](#geolayer-usefully-functions)
* [Write geolayer in GIS file](#write-geolayer-in-gis-file)
  * [Geoforamt GIS drivers](#geoforamt-gis-drivers)
  * [Make a GIS format transormation (shapefile => geojson)](#make-a-gis-format-transormation-shapefile--geojson)


### Create geoformat objects

When you use Geoformat, there are two basic objects:

* **feature**: the content. This object can store *attributes* and/or *geometry* data.
* **geolayer**: the container. It stores features. It is equivalent to a table in a database.


#### Create a feature

A feature contains attributes and geometry information. (For more technical information, see: [Geoformat Technical Description [WIP]](#geoformat-technical-description))

```python
# create a feature dict 
feature = {}

# add attributes data
feature['attributes'] = {'integer_field': 1704, 'string_field': 'hello world', 'real_list_field': [123.43, 65., 356.65]}

# add geometry data
feature['geometry'] = {'type': 'Point', 'coordinates': [2.34886039, 48.85332408]}

print(feature)

# >>> {'attributes': {'integer_field': 1704, 'string_field': 'hello world', 'real_list_field': [123.43, 65.0, 356.65]}, 'geometry': {'type': 'Point', 'coordinates': [2.34886039, 48.85332408]}}
```

#### Create a geolayer

A geolayer is an equivalent to a file or a table in database containing one or several features with attibutes and/or
geometry. (For more technical information, see: [Geoformat Technical Description [WIP]](#geoformat-technical-description))

##### handmade

```python
# first create geolayer dict with 'metadata' keys and features 'keys'
geolayer = {"metadata": {"name": "handmade geolayer"}, "features": {}}

# create fields metadata
metadata_fields = {
    "id": {"type": "Integer", "index": 0}, 
    "foo": {"type": "String", "width": 50, "index": 1}
}

# create geometry metadata
metadata_geometry = {"type": {"Point", "LineString"}, "crs": 4326}

# rattach fields metadata and geometry metadata to geolayer metadata
geolayer["metadata"]["fields"] = metadata_fields
geolayer["metadata"]["geometry_ref"] = metadata_geometry

# create features
feature_a = {"attributes": {"id": 8754, "foo": "bar"}, "geometry": {"type": "Point", "coordinates": [2.3488, 48.8533]}}
feature_b = {"attributes": {"id": 764, "foo": "baz"}, "geometry": {"type": "LineString", "coordinates": [[-2.1368, 47.2829], [-1.5655, 47.1971],  [3.9097, 44.8938]]}}

# rattach features to geolayer
geolayer['features'][0] = feature_a
geolayer['features'][1] = feature_b

print(geolayer)

# >>> {'metadata': {'name': 'handmade geolayer', 'fields': {'id': {'type': 'Integer', 'index': 0}, 'foo': {'type': 'String', 'width': 50, 'index': 1}}, 'geometry_ref': {'type': {'LineString', 'Point'}, 'crs': 4326}}, 'features': {0: {'attributes': {'id': 8754, 'foo': 'bar'}, 'geometry': {'type': 'Point', 'coordinates': [2.3488, 48.8533]}}, 1: {'attributes': {'id': 764, 'foo': 'baz'}, 'geometry': {'type': 'LineString', 'coordinates': [[-2.1368, 47.2829], [-1.5655, 47.1971], [3.9097, 44.8938]]}}}}
```

##### Using a driver

```python
import geoformat

departement_path = 'data/FRANCE_IGN/DEPARTEMENT_2016_L93.shp'

geolayer = geoformat.shapefile_to_geolayer(departement_path)

print(len(geolayer['features']))

# >>> 96
```

#### Print data geolayer

Sometimes it can be useful to print in terminal geolayer's attributes.

##### Print fields metadata

```python
import geoformat

region_path = 'data/FRANCE_IGN/REGION_2016_L93.shp'

geolayer = geoformat.shapefile_to_geolayer(region_path)

print(geoformat.print_metadata_field_table(geolayer))

# >>>
# +------------+---------+-------+-----------+-------+
# | field name | type    | width | precision | index |
# +============+=========+=======+===========+=======+
# | CODE_REG   | String  | 2     | None      | 0     |
# | NOM_REG    | String  | 35    | None      | 1     |
# | POPULATION | Integer | None  | None      | 2     |
# | SUPERFICIE | Integer | None  | None      | 3     |
# +------------+---------+-------+-----------+-------+
```


##### Print features data

```python
import geoformat

region_path = 'data/FRANCE_IGN/REGION_2016_L93.shp'

geolayer = geoformat.shapefile_to_geolayer(region_path)

print(geoformat.print_features_data_table(geolayer))

# ### >>>
# +--------+----------+-------------------------------------+------------+------------+--------------+--------------------------------+
# | i_feat | CODE_REG | NOM_REG                             | POPULATION | SUPERFICIE | type         | coordinates                    |
# +========+==========+=====================================+============+============+==============+================================+
# | 0      | 76       | LANGUEDOC-ROUSSILLON-MIDI-PYRENEES  | 5683878    | 7243041    | MultiPolygon | [[[[449862.6000001011, ...]]]] |
# | 1      | 75       | AQUITAINE-LIMOUSIN-POITOU-CHARENTES | 5844177    | 8466821    | MultiPolygon | [[[[547193.100000056,  ...]]]] |
# | 2      | 84       | AUVERGNE-RHONE-ALPES                | 7757595    | 7014795    | Polygon      | [[[831613.6999999505, 6 ...]]] |
# | 3      | 32       | NORD-PAS-DE-CALAIS-PICARDIE         | 5987883    | 3187435    | Polygon      | [[[608820.0000000052, 7 ...]]] |
# | 4      | 44       | ALSACE-CHAMPAGNE-ARDENNE-LORRAINE   | 5552388    | 5732928    | Polygon      | [[[776081.0999999898, 6 ...]]] |
# | 5      | 93       | PROVENCE-ALPES-COTE D'AZUR          | 4953675    | 3155736    | MultiPolygon | [[[[1009696.399999884, ...]]]] |
# | 6      | 27       | BOURGOGNE-FRANCHE-COMTE             | 2819783    | 4746283    | Polygon      | [[[826122.1999999635, 6 ...]]] |
# | 7      | 52       | PAYS DE LA LOIRE                    | 3660852    | 2997777    | MultiPolygon | [[[[396406.200000058,  ...]]]] |
# | 8      | 28       | NORMANDIE                           | 3328364    | 2728511    | MultiPolygon | [[[[414934.20000005106 ...]]]] |
# | 9      | 11       | ILE-DE-FRANCE                       | 11959807   | 1205191    | Polygon      | [[[607657.2000000161, 6 ...]]] |
# | 10     | 24       | CENTRE-VAL DE LOIRE                 | 2570548    | 3905914    | Polygon      | [[[690565.4000000022, 6 ...]]] |
# | 11     | 53       | BRETAGNE                            | 3258707    | 2702269    | MultiPolygon | [[[[263628.30000009853 ...]]]] |
# | 12     | 94       | CORSE                               | 320208     | 875982     | MultiPolygon | [[[[1232225.1999997576 ...]]]] |
# +--------+----------+-------------------------------------+------------+------------+--------------+--------------------------------+
```

#### Draw a Geometry

Functions have been developed to give you an overview of the geometries you are manipulating.
It is possible to view a geometry, a geometry present in an `Feature`, or all the geometries present in a `Geolayer`.

##### Draw a geometry

Here is a representation of a polygon. You can optionally add a graticule with the graticule parameter set to `True` (by default, this option is set to `False`).

```python
import geoformat

from tests.data.geometries import polygon_square_with_holes


geoformat.draw_geometry(polygon_square_with_holes, graticule=True)
```

This function will return this : 

![](https://framagit.org/Guilhain/Geoformat/-/raw/master/images/polygon_square_with_holes.png)

##### Draw a geometry in a feature

If there is a geometry within a feature, you can use `draw_feature` to have a graphical view of the geometry.

```python 
import geoformat

from tests.data.features import feature_katsuragawa

geoformat.draw_feature(feature_katsuragawa, graticule=True)
```

This function will return this : 

![](https://framagit.org/Guilhain/Geoformat/-/raw/master/images/katsuragawa.png)


##### Draw a geolayer

To view all geometries present in a geoLayer, you can use the `draw_geoLayer` function.

```python
import geoformat

from tests.data.geolayers import geolayer_idf_reseau_ferre

geoformat.draw_geolayer(geolayer_idf_reseau_ferre, graticule=True)
```

this function will return this : 
![](https://framagit.org/Guilhain/Geoformat/-/raw/master/images/idf_reseau_ferre.png)


### Geometry usefully functions

#### Area, length, distance, bbox and centroid

* [Area](#area)
* [Length](#length)
* [Distance](#distance)
* [Bbox](#bbox)
* [Centroid](#centroid)
  * [Euclidean distance](#euclidean-distance)
  * [Manhattan distance](#manhattan-distance)

##### Area

```python
import geoformat

geometry = {
    "type": "Polygon",
    "coordinates": [[[273950.31, 6643295.0], [190786.82, 6599267.27], [190786.82, 6467184.09], [44027.73, 6408480.45], [4891.97, 6364452.72], [39135.76, 6335100.9], [-122299.25, 6315533.03], [-141867.12, 6388912.57], [-200570.76, 6388912.57], [-176110.91, 6315533.03], [-151651.06, 6207909.69], [-288626.22, 6183449.84], [-337545.92, 6237261.51], [-513656.83, 6217693.63], [-528332.74, 6163881.96], [-489196.98, 6168773.93], [-469629.1, 6134530.14], [-513656.83, 6119854.23], [-484305.01, 6061150.59], [-450061.22, 6105178.32], [-313086.07, 6056258.63], [-225030.61, 5953527.26], [-249490.46, 5929067.41], [-136975.15, 5826336.04], [-112515.31, 5743172.56], [-73379.55, 5640441.19], [-127191.22, 5699144.83], [-127191.22, 5523033.92], [-195678.79, 5356706.94], [63595.61, 5258867.55], [73379.55, 5293111.33], [210354.7, 5229515.73], [362005.77, 5214839.82], [327761.98, 5307787.24], [464737.13, 5390950.73], [547900.62, 5386058.76], [665307.89, 5327355.12], [719119.56, 5342031.03], [841418.81, 5420302.55], [846310.78, 5479006.19], [782715.17, 5488790.13], [748471.38, 5625765.28], [777823.2, 5718712.71], [768039.26, 5836119.98], [684875.77, 5782308.32], [679983.8, 5860579.83], [758255.32, 5938851.35], [841418.81, 6031798.78], [851202.75, 6114962.26], [914798.35, 6271505.3], [748471.38, 6291073.18], [714227.59, 6354668.78], [635956.08, 6344884.84], [513656.83, 6447616.21], [322870.01, 6555239.55], [273950.31, 6643295.0]]]
}

geom_area = geoformat.geometry_area(geometry)

print(geom_area)

# >>> 1126425592118.5842
```

##### Length

```python
import geoformat

geometry = {
    "type": "Polygon",
    "coordinates": [[[273950.31, 6643295.0], [190786.82, 6599267.27], [190786.82, 6467184.09], [44027.73, 6408480.45], [4891.97, 6364452.72], [39135.76, 6335100.9], [-122299.25, 6315533.03], [-141867.12, 6388912.57], [-200570.76, 6388912.57], [-176110.91, 6315533.03], [-151651.06, 6207909.69], [-288626.22, 6183449.84], [-337545.92, 6237261.51], [-513656.83, 6217693.63], [-528332.74, 6163881.96], [-489196.98, 6168773.93], [-469629.1, 6134530.14], [-513656.83, 6119854.23], [-484305.01, 6061150.59], [-450061.22, 6105178.32], [-313086.07, 6056258.63], [-225030.61, 5953527.26], [-249490.46, 5929067.41], [-136975.15, 5826336.04], [-112515.31, 5743172.56], [-73379.55, 5640441.19], [-127191.22, 5699144.83], [-127191.22, 5523033.92], [-195678.79, 5356706.94], [63595.61, 5258867.55], [73379.55, 5293111.33], [210354.7, 5229515.73], [362005.77, 5214839.82], [327761.98, 5307787.24], [464737.13, 5390950.73], [547900.62, 5386058.76], [665307.89, 5327355.12], [719119.56, 5342031.03], [841418.81, 5420302.55], [846310.78, 5479006.19], [782715.17, 5488790.13], [748471.38, 5625765.28], [777823.2, 5718712.71], [768039.26, 5836119.98], [684875.77, 5782308.32], [679983.8, 5860579.83], [758255.32, 5938851.35], [841418.81, 6031798.78], [851202.75, 6114962.26], [914798.35, 6271505.3], [748471.38, 6291073.18], [714227.59, 6354668.78], [635956.08, 6344884.84], [513656.83, 6447616.21], [322870.01, 6555239.55], [273950.31, 6643295.0]]]
}

geom_length = geoformat.geometry_length(geometry)

print(geom_length)
# >>> 5999094.432367001
```
##### Distance

You can compute the distance between two points. There are two types of distance allowed:
- Euclidean
- Manhattan

##### Bbox

Each geometry has an associated bbox. The bbox represents the minimum bounding rectangle in which the geometry is embedded.

```python
import geoformat

polygon_geometry = {"type": "Polygon", "coordinates": [
    [[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]],
    [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]],
]}

polygon_bbox = geoformat.geometry_to_bbox(polygon_geometry)

print(polygon_bbox)

# >>> (-120.43, -20.28, 23.194, 57.322)
```
##### Centroid

You can get the centroid coordinates, which is the mean of all coordinates of a geometry.

```python
import geoformat

multi_point_coordinates  = [[-155.52, 19.61], [-156.22, 20.74], [-157.97, 21.46]]

multi_point_centroid = geoformat.coordinates_to_centroid(multi_point_coordinates)

print(multi_point_centroid)

# >>> [-156.57000000000002, 20.60333333333333]
```


###### Euclidean distance

```python
import geoformat

point_a = (0, 0)
point_b = (1, 1)

print(geoformat.euclidean_distance(point_a, point_b))

# >>> 1.4142135623730951
```


###### Manhattan distance

```python
import geoformat

point_a = (0, 0)
point_b = (1, 1)

print(geoformat.manhattan_distance(point_a, point_b))

# >>> 2.0
```

#### Reproject 

You can reproject an entire Geolayer or a simple geometry. To do that, indicate the input EPSG and the desired EPSG for the output.

* [Reproject Geometry](#reproject-geometry)
* [Reproject Geolayer](#reproject-geolayer)

##### Reproject Geometry

```python
import geoformat

point_geometry_4326 = {"type": "Point", "coordinates": [-115.81, 37.24]}

point_geometry_3857 = geoformat.reproject_geometry(point_geometry_4326, 4326, 3857)

print(point_geometry_3857)

# >>> {'type': 'Point', 'coordinates': [-12891910.228769012, 4472612.698469004]}
```

##### Reproject Geolayer

In this example, we will transform a geolayer from the Lambert93 projection [EPSG:2154] to the WGS84 coordinate system [EPSG:4326].

```python
import geoformat

region_path = 'data/FRANCE_IGN/REGION_2016_L93.shp'

geolayer = geoformat.shapefile_to_geolayer(region_path)

geolayer = geoformat.reproject_geolayer(geolayer, in_crs=2154, out_crs=4326)

print(geolayer['metadata']['geometry_ref']['crs'])

# >>>4326
```

#### Geometry formatting

* [wkb_to_geometry](#wkb_to_geometry)
* [geometry_to_wkb](#geometry_to_wkb)
* [wkt_to_geometry](#wkt_to_geometry)
* [geometry_to_wkt](#geometry_to_wkt)

##### wkb_to_geometry

You can convert geometry in WKB format to Geoformat geometry.

```python
import geoformat

geoformat_geometry = geoformat.wkb_to_geometry(b"\x00\x00\x00\x00\x01\xc0\\\xf3\xd7\n=p\xa4@B\x9e\xb8Q\xeb\x85\x1f")

print(geoformat_geometry)

# >>>  {"type": "Point", "coordinates": [-115.81, 37.24], "bbox": (-115.81, 37.24, -115.81, 37.24)}
```

##### geometry_to_wkb

You can convert Geoformat geometry to WKB format.

```python
import geoformat

wkb_geometry = geoformat.geometry_to_wkb({"type": "Point", "coordinates": [-115.81, 37.24]})

print(wkb_geometry)

# >>> b"\x00\x00\x00\x00\x01\xc0\\\xf3\xd7\n=p\xa4@B\x9e\xb8Q\xeb\x85\x1f"
```

##### wkt_to_geometry

From WKT geometry, you can make a conversion to Geoformat geometry.

```python
import geoformat

geoformat_geometry = geoformat.wkt_to_geometry("POINT (-115.81 37.24)")

print(geoformat_geometry)

# >>>  {"type": "Point", "coordinates": [-115.81, 37.24], "bbox": (-115.81, 37.24, -115.81, 37.24)}
```

##### geometry_to_wkt

Convert a geometry to WKT.

```python
import geoformat

wkt_geometry = geoformat.geometry_to_wkt({"type": "Point", "coordinates": [-115.81, 37.24]})

print(wkt_geometry)

# >>> "POINT (-115.81 37.24)"
```

#### Geometrics manipulations

In this section, we will present the functions for performing geometric operations.

* [Generalization](#generalization)
  * [Ramer Douglas Peucker](#ramer-douglas-peucker)
  * [Visvalimgam Whyatt](#visvalimgam-whyatt)
* [Merging geometries](#merging-geometries)
  * [LineString merging](#linestring-merging)
  * [Geometry merging](#geometry-merging)
* [Point on Linestring](#point-on-linestring)
* [Force rhr](#force-rhr)
* [Multi and single geometry](#multi-and-single-geometry)
  * [single_geometry_to_multi_geometry](#single_geometry_to_multi_geometry)
  * [multi_geometry_to_single_geometry](#multi_geometry_to_single_geometry)

##### Generalization

Geoformat allows cartographic generalization via the _simplify_ function by allowing the user to choose between two algorithms: 
* Ramer-Douglas-Peucker (RDP)
* Visvalingam-Whyatt (VW)

###### Ramer-Douglas-Peucker

The Ramer-Douglas-Peucker algorithm is a geometric simplification technique that reduces the number of points in a geometry while maintaining its overall shape.
It recursively subdivides the polyline, retaining points that exceed a specified distance tolerance.

Advantages:

* Preserves overall shape.
* Efficient for simple or mildly complex geometry.
* Easy to implement.

Disadvantages:

* Can produce suboptimal results for densely packed points.
* Slower for highly complex geometries.
* Fixed tolerance might not suit varying data densities.

```python
import geoformat

loire_geometry = {"type": "LineString", "coordinates": [[-237872.03, 5988382.54], [-209743.21, 5987159.55], [-198124.78, 5976152.62], [-174276.42, 5974318.13], [-154097.05, 5986548.06], [-145536.1, 5998777.98], [-119241.76, 6002446.96], [-104565.85, 6003669.95], [-88055.46, 6004281.45], [-78271.52, 6004281.45], [-66653.09, 6009173.42], [-52588.68, 6009173.42], [-37301.27, 6009173.42], [-32409.3, 6008561.92], [-23236.86, 5996331.99], [-4891.97, 5983490.57], [9172.44, 5977987.11], [18344.89, 5980433.09], [48919.7, 5996943.49], [67264.58, 6001223.96], [91724.43, 6009784.91], [116184.28, 6010396.41], [149205.08, 6032410.27], [155320.04, 6045863.19], [181002.88, 6060539.1], [182225.88, 6071546.03], [194455.8, 6079495.48], [204851.24, 6083775.96], [218915.65, 6089890.92], [245209.99, 6084387.45], [257439.91, 6077049.5], [295352.68, 6051978.15], [307582.6, 6038525.23], [328984.97, 6018957.36], [317366.54, 5998166.48], [342437.89, 5969426.16], [344883.87, 5941297.33], [389523.1, 5912557.01], [409702.47, 5892377.64], [412759.95, 5881982.2], [426824.37, 5861802.83], [447615.24, 5848961.4], [451284.21, 5812271.63], [452507.21, 5782919.81], [448838.23, 5766409.41], [457399.18, 5755402.48], [469017.61, 5738280.59], [465348.63, 5710151.76], [473298.08, 5695475.85], [468406.11, 5678965.45], [461068.15, 5656951.59], [448838.23, 5654811.35], [437066.93, 5651753.87], [436608.31, 5643498.67], [435385.31, 5636772.21], [440583.03, 5624695.16], [434468.07, 5621943.43], [435538.19, 5617815.83], [437831.3, 5613229.61], [435232.44, 5604821.54]]}
loire_simplify_geometry = geoformat.simplify(
    geometry=loire_geometry,
    tolerance=5000, 
    algo='RDP'
)

print(loire_simplify_geometry)

# >>> {'type': 'LineString', 'coordinates': [[-237872.03, 5988382.54], [-174276.42, 5974318.13], [-145536.1, 5998777.98], [-37301.27, 6009173.42], [9172.44, 5977987.11], [48919.7, 5996943.49], [116184.28, 6010396.41], [149205.08, 6032410.27], [194455.8, 6079495.48], [218915.65, 6089890.92], [245209.99, 6084387.45], [295352.68, 6051978.15], [328984.97, 6018957.36], [317366.54, 5998166.48], [342437.89, 5969426.16], [344883.87, 5941297.33], [389523.1, 5912557.01], [426824.37, 5861802.83], [447615.24, 5848961.4], [448838.23, 5766409.41], [469017.61, 5738280.59], [465348.63, 5710151.76], [473298.08, 5695475.85], [461068.15, 5656951.59], [437066.93, 5651753.87], [435232.44, 5604821.54]]}
```

###### Visvalimgam Whyatt

The Visvalingam-Whyatt algorithm is a geometry simplification method that reduces the number of points while preserving shape. 
It iteratively removes points based on their "effective area," which is the triangular area formed by a point and its two neighbors.
The algorithm removes points with the smallest areas until a desired level of simplification is achieved.

Advantages:

* Better preservation of local features.
* More intuitive elimination based on effective area.
* Adaptive to varying data densities.

Disadvantages:

* Can be slower for large datasets.
* More complex to implement.
* Requires pre-sorting or priority queue for best performance.

```python
import geoformat

france_geometry = {
    "type": "Polygon",
    "coordinates":  [[[273950.31, 6643295.0], [190786.82, 6599267.27], [190786.82, 6467184.09], [44027.73, 6408480.45], [4891.97, 6364452.72], [39135.76, 6335100.9], [-122299.25, 6315533.03], [-141867.12, 6388912.57], [-200570.76, 6388912.57], [-176110.91, 6315533.03], [-151651.06, 6207909.69], [-288626.22, 6183449.84], [-337545.92, 6237261.51], [-513656.83, 6217693.63], [-528332.74, 6163881.96], [-489196.98, 6168773.93], [-469629.1, 6134530.14], [-513656.83, 6119854.23], [-484305.01, 6061150.59], [-450061.22, 6105178.32], [-313086.07, 6056258.63], [-225030.61, 5953527.26], [-249490.46, 5929067.41], [-136975.15, 5826336.04], [-112515.31, 5743172.56], [-73379.55, 5640441.19], [-127191.22, 5699144.83], [-127191.22, 5523033.92], [-195678.79, 5356706.94], [63595.61, 5258867.55], [73379.55, 5293111.33], [210354.7, 5229515.73], [362005.77, 5214839.82], [327761.98, 5307787.24], [464737.13, 5390950.73], [547900.62, 5386058.76], [665307.89, 5327355.12], [719119.56, 5342031.03], [841418.81, 5420302.55], [846310.78, 5479006.19], [782715.17, 5488790.13], [748471.38, 5625765.28], [777823.2, 5718712.71], [768039.26, 5836119.98], [684875.77, 5782308.32], [679983.8, 5860579.83], [758255.32, 5938851.35], [841418.81, 6031798.78], [851202.75, 6114962.26], [914798.35, 6271505.3], [748471.38, 6291073.18], [714227.59, 6354668.78], [635956.08, 6344884.84], [513656.83, 6447616.21], [322870.01, 6555239.55], [273950.31, 6643295.0]]],
}
france_simplify_geometry = geoformat.simplify(
    geometry=france_geometry,
    tolerance=3000000000, 
    algo='VW'
)

print(france_simplify_geometry)

# >>> {'type': 'Polygon', 'coordinates': [[[273950.31, 6643295.0], [190786.82, 6599267.27], [190786.82, 6467184.09], [44027.73, 6408480.45], [39135.76, 6335100.9], [-122299.25, 6315533.03], [-151651.06, 6207909.69], [-288626.22, 6183449.84], [-337545.92, 6237261.51], [-513656.83, 6217693.63], [-469629.1, 6134530.14], [-313086.07, 6056258.63], [-225030.61, 5953527.26], [-136975.15, 5826336.04], [-127191.22, 5699144.83], [-127191.22, 5523033.92], [-195678.79, 5356706.94], [63595.61, 5258867.55], [210354.7, 5229515.73], [362005.77, 5214839.82], [327761.98, 5307787.24], [464737.13, 5390950.73], [547900.62, 5386058.76], [665307.89, 5327355.12], [719119.56, 5342031.03], [841418.81, 5420302.55], [782715.17, 5488790.13], [748471.38, 5625765.28], [777823.2, 5718712.71], [768039.26, 5836119.98], [684875.77, 5782308.32], [679983.8, 5860579.83], [758255.32, 5938851.35], [841418.81, 6031798.78], [851202.75, 6114962.26], [914798.35, 6271505.3], [748471.38, 6291073.18], [635956.08, 6344884.84], [513656.83, 6447616.21], [322870.01, 6555239.55], [273950.31, 6643295.0]]]}
```


##### Merging geometries

###### LineString merging

This function is similar than [ST_LineMerge](https://postgis.net/docs/ST_LineMerge.html) from Postgis. 
You can optionaly choose to not allow reverse geometry when setting `directed` to True.  This is useful when dealing 
with a road network where the direction in which the coordinates are encoded is important for defining the direction of 
traffic.)

```python
import geoformat 

multi_line_geometry = {
            "type": "MultiLineString",
            "coordinates": [
                [[2, 3], [5, 2], [8, 4]],
                [[5, 9], [3, 6]],
                [[3, 6], [2, 3]],
                [[8, 4], [9, 7], [5, 9]],
            ],
        }

line_merged_geometry = geoformat.line_merge(geometry=multi_line_geometry)

print(line_merged_geometry)

# >>> {"type": "LineString", "coordinates": [[8, 4], [9, 7], [5, 9], [3, 6], [2, 3], [5, 2], [8, 4]]}
```

Example with directed linestring.
```python
import geoformat 

multi_line_geometry = {
  "type": "MultiLineString",
  "coordinates": [
    [[0, 0], [0, 10],],
    [[0, 10], [0, 20]],
    [[0, 30], [0, 20]]
    ]
}

line_merged_geometry = geoformat.line_merge(geometry=multi_line_geometry, directed=True)

print(line_merged_geometry)

# >>> {'type': 'MultiLineString', 'coordinates': [[[0, 0], [0, 10], [0, 20]], [[0, 30], [0, 20]]]}
```

###### Geometry merging

Return the result of merging two different geometries by adding them together. Please note that this function does not "union" two geometries that intersect. It simply adds one geometry to another.

Here is an example of merging combinations:

- Single AND Single
  * `Point` + `Point` = `MultiPoint`
  * `LineString` + `LineString` = `MultiLineString`
  * `Polygon` + `Polygon` = `MultiPolygon` 

- Single AND Multi 
  * `Point` + `MultiPoint` = `MultiPoint` 
  * `LineString`  + `MultiLineString` = `MultiLineString`
  * `Polygon` + `MultiPolygon` = `MultiPolygon`

- Mixed Geometries Types and GeometryCollection
  * `Point` + `Polygon` = `GeometryCollection(Point, Polygon)`
  * `GeometryCollection(Polygon + LineString)` + `LineSting` = `GeometryCollection(Polygon + MultiLineString)`
  * `GeometryCollection(MultiPolygon, LineString), GeometryCollection(MultiPoint, LineString)` = `GeometryCollection(MultiPolygon, MultiLineString, MultiPoint)`

```python
import geoformat

geometry_a = {"type": "Point", "coordinates": [-115.81, 37.24]}
geometry_b = {"type": "Polygon", "coordinates": [
    [[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]],
    [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]],
]}

merged_geometry = geoformat.merge_geometries(geometry_a, geometry_b, bbox=False)

print(merged_geometry)

# >>> {'type': 'GeometryCollection', 'geometries': [{'type': 'Point', 'coordinates': [-115.81, 37.24]}, {'type': 'Polygon', 'coordinates': [[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]], [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]]}]}
```


##### Point on Linestring


If you want to add point(s) on a linestring at a given distance, points_on_linestring_distance is for you. 
You can optionally add an offset that will shift each point created to the left (positive offset) or right (negative offset) of the line depending on the direction of the line.

```python
import geoformat

linestring_geometry =  {
    "type": "LineString",
    "coordinates": [[-10, -10], [-10, 10], [10, 10]],
}

point_on_linestring_gen = geoformat.points_on_linestring_distance(linestring_geometry, 5)

for point in point_on_linestring_gen:
    print(point)

# >>> {'type': 'Point', 'coordinates': [-10, -10]}
# >>> {'type': 'Point', 'coordinates': [-10, -5]}
# >>> {'type': 'Point', 'coordinates': [-10, 0]}
# >>> {'type': 'Point', 'coordinates': [-10, 5]}
# >>> {'type': 'Point', 'coordinates': [-10, 10]}
# >>> {'type': 'Point', 'coordinates': [-5.0, 10.0]}
# >>> {'type': 'Point', 'coordinates': [0.0, 10.0]}
# >>> {'type': 'Point', 'coordinates': [5.0, 10.0]}
# >>> {'type': 'Point', 'coordinates': [10.0, 10.0]}
```


Same with offset:

```python
import geoformat

linestring_geometry =  {
    "type": "LineString",
    "coordinates": [[-10, -10], [-10, 10], [10, 10]],
}

point_on_linestring_offset_gen = geoformat.points_on_linestring_distance(linestring_geometry, 5, -10)

for point in point_on_linestring_offset_gen:
    print(point)

# >>> {'type': 'Point', 'coordinates': [-20.0, -10.0]}
# >>> {'type': 'Point', 'coordinates': [-20.0, -5.0]}
# >>> {'type': 'Point', 'coordinates': [-20.0, 0.0]}
# >>> {'type': 'Point', 'coordinates': [-20.0, 5.0]}
# >>> {'type': 'Point', 'coordinates': [-20.0, 10.0]}
# >>> {'type': 'Point', 'coordinates': [-5.0, 0.0]}
# >>> {'type': 'Point', 'coordinates': [0.0, 0.0]}
# >>> {'type': 'Point', 'coordinates': [5.0, 0.0]}
# >>> {'type': 'Point', 'coordinates': [10.0, 0.0]}
```

##### Force rhr


Force the orientation of the vertices in a polygon to follow the Right-Hand-Rule, in which the area bounded by the polygon is to the right of the boundary. Specifically, the exterior ring is oriented in a clockwise direction, and the interior rings are oriented in a counter-clockwise direction.

``` python
import geoformat

polygon = {'type': 'Polygon',
           'coordinates': [[[0, 0], [5, 0], [0, 5], [0, 0]],
                           [[1, 1], [1, 3], [3, 1], [1, 1]]]}
                                             
                                             
polygon_rhr = geoformat.force_rhr(polygon)

print(polygon_rhr)

# >>> {'type': 'Polygon', 'coordinates': [[[0, 0], [0, 5], [5, 0], [0, 0]], [[1, 1], [3, 1], [1, 3], [1, 1]]]}
```

##### Multi and single geometry

As you know, there are single and multi geometries:

**Single geometry:**
- `Point`
- `LineString`
- `Polygon`

**Multi geometry:**
- `MultiPoint`
- `MultiLineString`
- `MultiPolygon`

There are two functions for switching from one to the other: `single_geometry_to_multi_geometry` and `multi_geometry_to_single_geometry`.


###### single_geometry_to_multi_geometry

```python
import geoformat

polygon = {"type": "Polygon", "coordinates": [
        [[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]],
        [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]],
    ]
}

multi_polygon = geoformat.single_geometry_to_multi_geometry(polygon)

print(multi_polygon)

# >>> {'type': 'MultiPolygon', 'coordinates': [[[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]], [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]]]}
```

###### multi_geometry_to_single_geometry

This function returns a generator with single geometries of multi geometry in each iteration.

```python
import geoformat

multi_geometry = {
    "type": "MultiLineString",
    "coordinates": [
        [[3.75, 9.25], [-130.95, 1.52]],
        [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]],
    ],
}

for geometry in geoformat.multi_geometry_to_single_geometry(multi_geometry):
    print(geometry)

# >>> {'type': 'LineString', 'coordinates': [[3.75, 9.25], [-130.95, 1.52]]}
# >>> {'type': 'LineString', 'coordinates': [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]]}
```

#### Low level geometrics objects


There are low-level geometric objects that compose or describe the geometries generally used in GIS (point, linestring, polygon, etc.).
It is with these low-level geometric objects that we calculate the existing interactions between the GIS geometries.
For more details, refer to the technical documentation : [Geoformat Technical Description [WIP]](#geoformat-technical-description).

* [point, segment and bbox](#point-segment-and-bbox)
  * [point_intersects_point](#point_intersects_point)
  * [point_intersects_segment](#point_intersects_segment)
  * [point_intersects_bbox](#point_intersects_bbox)
  * [segment_intersects_segment](#segment_intersects_segment)
  * [segment_intersects_bbox](#segment_intersects_bbox)
  * [bbox_intersects_bbox](#bbox_intersects_bbox)
  * [ccw_or_cw_segments](#ccw_or_cw_segments)
  * [point_position_segment](#point_position_segment)
  * [extent_bbox](#extent_bbox)
  * [bbox_union](#bbox_union)
  * [point_bbox_position](#point_bbox_position)
  * [random](#random)
* [Line](#line)
  * [line_parameters](#line_parameters)
  * [perpendicular_line_parameters_at_point](#perpendicular_line_parameters_at_point)
  * [point_at_distance_with_line_parameters](#point_at_distance_with_line_parameters)
  * [crossing_point_from_lines_parameters](#crossing_point_from_lines_parameters)

##### point, segment and bbox

###### point_intersects_point

Check if two points are similar.

```python
import geoformat

point_a = (10, 10)
point_b = (10, 10)
pt_a_int_pt_b = geoformat.point_intersects_point(point_a, point_b)

print(pt_a_int_pt_b)

# >>> True
```

###### point_intersects_segment

Check if a point intersects a segment.

```python
import geoformat

point =  (0, 0)
segment = ((-10, -10), (10, 10))

pt_int_seg = geoformat.point_intersects_segment(point, segment)

print(pt_int_seg)

# >>> True
```


###### point_intersects_bbox

Check if a point is in a bounding box (bbox).

```python
import geoformat

point =  (0, 0)
bbox = (-10, -10, 10, 10)

pt_int_bbx = geoformat.point_intersects_bbox(point, bbox)

print(pt_int_bbx)

# >>> True
```

###### segment_intersects_segment

Check if a segment intersects another segment.

```python
import geoformat

segment_a = ((10, 10), (-10, -10))
segment_b = ((-10, 10), (10, -10))

seg_int_seg = geoformat.segment_intersects_segment(segment_a, segment_b)

print(seg_int_seg)

# >>> True
```

###### segment_intersects_bbox

Check if a segment intersects a bounding box (bbox).

```python
import geoformat

segment = ((-2, 0), (2, 0))
bbox = (-10, -10, 10, 10)

seg_int_bbx = geoformat.segment_intersects_bbox(segment, bbox)

print(seg_int_bbx)

# >>> True
```

###### bbox_intersects_bbox

Check if two bounding boxes (bbox) intersect.

```python
import geoformat

bbox_a = (-10, -10, 10, 10)
bbox_b = (-10, -10, 10, 10)

bbx_int_bbx = geoformat.bbox_intersects_bbox(bbox_a, bbox_b)

print(bbx_int_bbx)

# >>> True
```

###### ccw_or_cw_segments

Check if two continuous segments are clockwise ('CW') or counterclockwise ('CCW').

Counter-clockwise example:

```python
import geoformat

segment_a = ((-5, -5), (5, 5))
segment_b =  ((5, 5), (-1, 2))

seg_a_and_seg_b_clock_wise = geoformat.ccw_or_cw_segments(segment_a, segment_b)

print(seg_a_and_seg_b_clock_wise)

# >>> 'CCW'
```

Clockwise example:

```python
import geoformat

segment_a = ((-5, -5), (5, 5))
segment_b = ((5, 5), (5, -5))

seg_a_and_seg_b_clock_wise = geoformat.ccw_or_cw_segments(segment_a, segment_b)

print(seg_a_and_seg_b_clock_wise)

# >>> 'CCW'
```

###### point_position_segment

Give the position of a point with respect to the direction of a segment. There are three possible positions: 
- `LEFT`
- `RIGHT` 
- `NEITHER`

Left example : 
```python
import geoformat

segment = ((-5, -5), (5, 5))
point =  (-1, 2)

pt_vs_seg_position = geoformat.point_position_segment(point, segment)

print(pt_vs_seg_position)

# >>> 'LEFT'
```

right example :
```python
import geoformat

segment = ((-5, -5), (5, 5))
point = (5, -5)

pt_vs_seg_position = geoformat.point_position_segment(point, segment)

print(pt_vs_seg_position)

# >>> 'RIGHT'
```

neither example :
```python
import geoformat

segment = ((-5, -5), (5, 5))
point = (10, 10)

pt_vs_seg_position = geoformat.point_position_segment(point, segment)

print(pt_vs_seg_position)

# >>> 'NEITHER'
```

###### bbox_expand

Expand a bounding box (bbox).

```python
import geoformat

bbox = (-1, -1, 1, 1)
bbox_expanded = geoformat.bbox_expand(bbox, 10)

print(bbox_expanded)

# >>> (-11, -11, 11, 11)
```
###### bbox_union

Union two bounding boxes (bbox).

```python
import geoformat

bbox_a = (-10, -10, 0, 0)
bbox_b = (0, 0, 10, 10)

bbox_unioned = geoformat.bbox_union(bbox_a, bbox_b)

print(bbox_unioned)

# >>> (-10, -10, 10, 10)
```

###### point_bbox_position

Gives the position of a point relative to a bounding box (bbox).
This function returns 2 main pieces of information:
1. If the point is localized in the Exterior, Interior, or on the bbox Boundary
2. The place of the frame where the point is located (NW, N, NE, W, E, SW, S, SE)

```ascii 
   NW  |   N  |  NE
-------+------+-------
    W  | bbox |   E
-------+------+-------
   SW  |   S  |  SE
```

Point localized on the bbox North-West (NW) corner.

```python
import geoformat

point = (-10, 10)
bbox = (-10, -10, 10, 10)

point_position = geoformat.point_bbox_position(point, bbox)

print(point_position)

# >>> ('Boundary', 'NW')
```

Point localised in bounding boxes (bbox).
```python
import geoformat

point = (0, 0)
bbox = (-10, -10, 10, 10)

point_position = geoformat.point_bbox_position(point, bbox)

print(point_position)

# >>> ('Interior', None)
```


Point localised in South (S) of bounding boxes (bbox).
```python
import geoformat
        
point = (0, -11)
bbox = (-10, -10, 10, 10)

point_position = geoformat.point_bbox_position(point, bbox)

print(point_position)

# >>> ('Exterior', 'S')
```

###### random


These three low-level geometric objects can be created randomly. You must specify a bounding box (bbox) within which these objects will be created. 
Optionally, you can specify the number of digits after the decimal point for each coordinate.

####### random_point

```python
import geoformat

bbox = (-180, -90, 180, 90)
random_point = geoformat.random_point(bbox)

print(random_point)

# >>> (59.89, 1.04)
```

####### random_segment


```python
import geoformat

bbox = (-180, -90, 180, 90)
random_segment = geoformat.random_segment(bbox)

print(random_segment)

# >>> ((-155.78, 82.55), (99.11, -17.46))
```

####### random_bbox

```python
import geoformat

bbox = (-180, -90, 180, 90)
random_bbox = geoformat.random_bbox(bbox)

print(random_bbox)

# >>> (-63.44, -87.6, -16.79, 15.78)

```


##### Line

Geoformat lets you use the concept of a line.

A line is an infinite, one-dimensional entity made up of an infinite succession of aligned points. It is defined by its constituent points as a mathematical equation in the form: y = mx + c

###### line_parameters

A line is defined by two pieces of information:
* slope: characterizes the slope of the line. (if the line is vertical, this parameter is 'VERTICAL')
* intercept: is the line y-intercept to the origin.

Example of a basic line:

```python
import geoformat

segment = ((645285, 6779558), (647006, 6779454))

line_param = geoformat.line_parameters(segment)

print(line_param)

# >>> {'slope': -0.06042998256827426, 'intercept': 6818552.5613015685}
```

example of horizontal line : 
```python
import geoformat

segment = ((-5, 1), (5, 1))

line_param = geoformat.line_parameters(segment)

print(line_param)

# >>> {'slope': 0.0, 'intercept': 1.0}
```

example of vertical line :
```python
import geoformat

segment = ((0, -5), (0, 5))

line_param = geoformat.line_parameters(segment)

print(line_param)

# >>> {'slope': 'VERTICAL', 'intercept': 0.0}
```

###### perpendicular_line_parameters_at_point

Return the perpendicular line parameters to a given point on a line.

```python
import geoformat

line_param = {'slope': 0.0, 'intercept': 0.0}
point = (0, 0)

perpendicular_line_param = geoformat.perpendicular_line_parameters_at_point(line_param, point)

print(perpendicular_line_param)

# >>> {'slope': 'VERTICAL', 'intercept': 0.}
```


###### point_at_distance_with_line_parameters

To create a point on a line at a distance from a reference point on the line.

```python
import geoformat

start_point = (0, 0)
line_parameters =  {'slope': 1, 'intercept': 0}
distance = 5

point_at_distance = geoformat.point_at_distance_with_line_parameters(start_point, line_parameters, distance)

print(point_at_distance)

# >>> (3.5355339059327373, 3.5355339059327373)
```

###### crossing_point_from_lines_parameters

How to find the crossing point between two lines?

```python
import geoformat

line_parameter_a = {'slope': 1, 'intercept': -2}
line_parameter_b = {'slope': -1, 'intercept': -3.}

crossing_point = geoformat.crossing_point_from_lines_parameters(line_parameter_a, line_parameter_b)

print(crossing_point)

# >>> (-0.5, -2.5)
```

#### Geometry Index and Matrix

Index and matrix allow for speeding up access to geometry for some geoprocessing.

* [Geometry Index](#geometry-index)
  * [Grid index](#grid-index)
* [Geometry Matrix](#geometry-matrix)
  * [Adjacency matrix](#adjacency-matrix)

##### Geometry Index


###### Grid index

You can create a grid index.

```python
import geoformat

from tests.data.geolayers import geolayer_for_index

geolayer_grd_idx = geoformat.create_grid_index(geolayer_for_index)

print(geolayer_grd_idx)

# >>> {'metadata': {'type': 'grid', 'mesh_size': 15.093333333333334, 'x_grid_origin': 0, 'y_grid_origin': 0, 'grid_precision': None}, 'index': {(-1, 0): [0, 1], (0, 0): [0, 1], (-1, -1): [1, 2], (0, -1): [1]}}
```


##### Geometry Matrix


###### Adjacency matrix

```python
import geoformat

from tests.data.geolayers import geolayer_grid_3_3

adjacency_mtx = geoformat.create_adjacency_matrix(geolayer_grid_3_3)

print(adjacency_mtx)

# >>> {'matrix': {0: {1, 3, 4}, 1: {0, 2, 3, 4, 5}, 2: {1, 4, 5}, 3: {0, 1, 4, 6, 7}, 4: {0, 1, 2, 3, 5, 6, 7, 8}, 5: {1, 2, 4, 7, 8}, 6: {3, 4, 7}, 7: {3, 4, 5, 6, 8}, 8: {4, 5, 7}}, 'metadata': {'type': 'adjacency'}}
```

### Attributes usefully functions

Attribute data is the second component of the information stored in a Geolayer.
Here, we'll take a look at the main functions for making the most of the attribute information contained in a Geolayer.

* [Attributes index](#attributes-index)
  * [Join geolayer attributes](#join-geolayer-attributes)
    * [full join](#full-join)
    * [join](#join)
    * [left join](#left-join)
    * [right join](#right-join)
  * [Clause functions](#clause-functions)
    * [clause where](#clause-where)
    * [clause group by](#clause-group-by)
    * [clause order by](#clause-order-by)
  * [Field statistics](#field-statistics)

#### Attributes index

The best way to access attribute data quickly and repeatedly is to create an attribute index. 
For the moment, only a hash table index is available via the function: `create_attribute_index`.
To associate the index created with a geolayer, use the `add_attribute_index` function.

```python
import geoformat

geolayer = geoformat.geojson_to_geolayer('data/doc/dept_population_extract.geojson')

geolayer_index = geoformat.create_attribute_index(geolayer, 'INSEE_REG')

print(geolayer_index)

geolayer = geoformat.add_attributes_index(geolayer, 'INSEE_REG', geolayer_index)

# >>> {'metadata': {'type': 'hashtable'}, 'index': {'75': [0], '52': [1], '32': [2]}}
```

#### Join geolayer attributes
Initially, the data is stored in a geolayer. Sometimes it's more practical to store data in several geolayers, and often we want to exchange/combine data between several geolayers. 
Attribute joins enable us to link one geolayer to another by means of a column containing information they have in common.

Geoformat offers four different types of attribute joins:
- Full join
- Inner join
- Left join
- Right join

The parameters can be transposed from one type to another, but the result in terms of returned entities will vary (see examples below).
- `field_name_filter_a` or `field_name_filter_b`: allows you to keep in the output geolayer only the fields of the specified geolayer.
- `rename_output_field_from_geolayer_a` or `rename_output_field_from_geolayer_b`: renames fields from input geolayer in the output geolayer. By default, renaming is automatic when a duplicate field name is detected.
- `geometry_ref`: A geolayer can only contain one geometry field, so the user must specify the geometry of which geolayer to keep. By default, the geometry from `geolayer_a` is kept (except for `join_right` where `geolayer_b` is the default value). If you want to keep the geometry of the second geolayer, just indicate `geolayer_b` for this parameter.

##### full join

The `join_full` function keeps the entirety of the features of each of the two geolayers to be joined. 
If there is no matching for a feature in the other geolayer, the fields in the other geolayer will have a None value.

```ascii
       *~~*   *~~*    
     *~~~~~*~~*~~~~~*  
    *~~A~~*~~~~*~~B~~*  
    *~~~~~*~~~~*~~~~~*
     *~~~~~*~~*~~~~~* 
        *~~*  *~~*
```

```python
import geoformat

from tests.data.geolayers import feature_list_data_and_geometry_geolayer_2
from tests.data.geolayers import feature_list_dpt_data_pop_geolayer

geolayer_full_join = geoformat.join_full(
    geolayer_a=feature_list_data_and_geometry_geolayer_2,
    geolayer_b=feature_list_dpt_data_pop_geolayer,
    on_field_a="CODE_DEPT",
    on_field_b="CODE_DEPT",
    output_geolayer_name= "FRANCE_DPT_FULL_JOIN",
)

print(geoformat.print_features_data_table(geolayer_full_join))

# >>>
# +--------+-----------+-------------+------------+-----------+------------+---------+---------+---------+--------------------------------+
# | i_feat | CODE_DEPT | NOM_DEPT    | CODE_DEPT1 | INSEE_REG | POPULATION | AREA    | DENSITY | type    | coordinates                    |
# +========+===========+=============+============+===========+============+=========+=========+=========+================================+
# | 0      | 53        | MAYENNE     | 53         | 52        | 307445     | 5208.37 | 59.03   | Polygon | [[[399495.0, 6830885.0] ...]]] |
# | 1      | 02        | AISNE       | 02         | 32        | 534490     | 7418.97 | 72.04   | Polygon | [[[776081.0, 6923412.0] ...]]] |
# | 2      | 02        | AISNE       | 02         | 32        | 534490     | 7418.97 | 72.04   | Polygon | [[[776081.0, 6923412.0] ...]]] |
# | 3      | 70        | HAUTE-SAONE | None       | None      | None       | None    | None    | Polygon | [[[986052.0, 6752778.0] ...]]] |
# | 4      | None      | None        | 87         | 75        | 374426     | 5549.31 | 67.47   | None    | None                           |
# | 5      | 53        | MAYENNE     | 53         | 52        | 307445     | 5208.37 | 59.03   | Polygon | [[[399495.0, 6830885.0] ...]]] |
# | 6      | 02        | AISNE       | 02         | 32        | 534490     | 7418.97 | 72.04   | Polygon | [[[776081.0, 6923412.0] ...]]] |
# | 7      | 02        | AISNE       | 02         | 32        | 534490     | 7418.97 | 72.04   | Polygon | [[[776081.0, 6923412.0] ...]]] |
# +--------+-----------+-------------+------------+-----------+------------+---------+---------+---------+--------------------------------+
```

##### join

On the other hand, `join` will only keep entities that are related to each other between two geolayers.

```ascii
       *  *   *  *    
     *     *~~*     *  
    *  A  *~~~~*  B  *  
    *     *~~~~*     *
     *     *~~*     * 
        *  *  *  *
```

```python
import geoformat

from tests.data.geolayers import feature_list_data_and_geometry_geolayer_2
from tests.data.geolayers import feature_list_dpt_data_pop_geolayer

geolayer_join = geoformat.join(
    geolayer_a=feature_list_data_and_geometry_geolayer_2,
    geolayer_b=feature_list_dpt_data_pop_geolayer,
    on_field_a="CODE_DEPT",
    on_field_b="CODE_DEPT",
    output_geolayer_name= "FRANCE_DPT_FULL_JOIN",
)

print(geoformat.print_features_data_table(geolayer_join))

# >>>
# +--------+-----------+----------+------------+-----------+------------+---------+---------+---------+--------------------------------+
# | i_feat | CODE_DEPT | NOM_DEPT | CODE_DEPT1 | INSEE_REG | POPULATION | AREA    | DENSITY | type    | coordinates                    |
# +========+===========+==========+============+===========+============+=========+=========+=========+================================+
# | 0      | 53        | MAYENNE  | 53         | 52        | 307445     | 5208.37 | 59.03   | Polygon | [[[399495.0, 6830885.0] ...]]] |
# | 1      | 02        | AISNE    | 02         | 32        | 534490     | 7418.97 | 72.04   | Polygon | [[[776081.0, 6923412.0] ...]]] |
# | 2      | 02        | AISNE    | 02         | 32        | 534490     | 7418.97 | 72.04   | Polygon | [[[776081.0, 6923412.0] ...]]] |
# +--------+-----------+----------+------------+-----------+------------+---------+---------+---------+--------------------------------+
```

```python
import geoformat

from tests.data.geolayers import feature_list_data_and_geometry_geolayer
from tests.data.geolayers import feature_list_dpt_data_pop_geolayer

geolayer_full_join = geoformat.join(
    geolayer_a=feature_list_data_and_geometry_geolayer,
    geolayer_b=feature_list_dpt_data_pop_geolayer,
    on_field_a="CODE_DEPT",
    on_field_b="CODE_DEPT",
    output_geolayer_name= "FRANCE_DPT_JOIN",
)

print(geoformat.print_features_data_table(geolayer_full_join))

# >>>
# +--------+-----------+----------+------------+-----------+------------+---------+---------+---------+--------------------------------+
# | i_feat | CODE_DEPT | NOM_DEPT | CODE_DEPT1 | INSEE_REG | POPULATION | AREA    | DENSITY | type    | coordinates                    |
# +========+===========+==========+============+===========+============+=========+=========+=========+================================+
# | 0      | 53        | MAYENNE  | 53         | 52        | 307445     | 5208.37 | 59.03   | Polygon | [[[399495.0, 6830885.0] ...]]] |
# | 1      | 02        | AISNE    | 02         | 32        | 534490     | 7418.97 | 72.04   | Polygon | [[[776081.0, 6923412.0] ...]]] |
# +--------+-----------+----------+------------+-----------+------------+---------+---------+---------+--------------------------------+
```

##### left join

The `join_left` function will keep all the features of the left geolayer and join them to the right geolayer. 
If an entity on the left corresponds to several entities on the right, then the entity on the left will be duplicated as many times.
If there is no matching for a feature in the other geolayer, the fields in the other geolayer will have a None value.

```ascii
       *~~*   *  *    
     *~~~~~*~~*     *  
    *~~A~~*~~~~*  B  *  
    *~~~~~*~~~~*     *
     *~~~~~*~~*     * 
        *~~*  *  *
```

```python
import geoformat

from tests.data.geolayers import feature_list_data_and_geometry_geolayer_2
from tests.data.geolayers import feature_list_dpt_data_pop_geolayer

geolayer_left_join = geoformat.join_left(
    geolayer_a=feature_list_data_and_geometry_geolayer_2,
    geolayer_b=feature_list_dpt_data_pop_geolayer,
    on_field_a="CODE_DEPT",
    on_field_b="CODE_DEPT",
    output_geolayer_name= "FRANCE_DPT_LEFT_JOIN",
    field_name_filter_a=['CODE_DEPT', 'NOM_DEPT'],
    field_name_filter_b=['INSEE_REG', 'POPULATION', 'AREA', 'DENSITY']
)

print(geoformat.print_features_data_table(geolayer_left_join))

# >>>
# +--------+-----------+-------------+-----------+------------+---------+---------+---------+--------------------------------+
# | i_feat | CODE_DEPT | NOM_DEPT    | INSEE_REG | POPULATION | AREA    | DENSITY | type    | coordinates                    |
# +========+===========+=============+===========+============+=========+=========+=========+================================+
# | 0      | 53        | MAYENNE     | 52        | 307445     | 5208.37 | 59.03   | Polygon | [[[399495.0, 6830885.0] ...]]] |
# | 1      | 02        | AISNE       | 32        | 534490     | 7418.97 | 72.04   | Polygon | [[[776081.0, 6923412.0] ...]]] |
# | 2      | 02        | AISNE       | 32        | 534490     | 7418.97 | 72.04   | Polygon | [[[776081.0, 6923412.0] ...]]] |
# | 3      | 70        | HAUTE-SAONE | None      | None       | None    | None    | Polygon | [[[986052.0, 6752778.0] ...]]] |
# +--------+-----------+-------------+-----------+------------+---------+---------+---------+--------------------------------+
```

##### right join

The `join_right` function will keep all the features of the right geolayer and join them to the left geolayer. 
If an entity on the right corresponds to several entities on the left, then the entity on the right will be duplicated as many times. 
If there is no matching for a feature in the other geolayer, the fields in the other geolayer will have a None value.

```ascii
       *  *   *~~*    
     *     *~~*~~~~~*  
    *  A  *~~~~*~~B~~*  
    *     *~~~~*~~~~~*
     *     *~~*~~~~~* 
        *  *  *~~*
```


```python
import geoformat

from tests.data.geolayers import feature_list_data_and_geometry_geolayer_2
from tests.data.geolayers import feature_list_dpt_data_pop_geolayer

geolayer_right_join = geoformat.join_right(
    geolayer_a=feature_list_data_and_geometry_geolayer_2,
    geolayer_b=feature_list_dpt_data_pop_geolayer,
    on_field_a="CODE_DEPT",
    on_field_b="CODE_DEPT",
    output_geolayer_name= "FRANCE_DPT_LEFT_JOIN",
    field_name_filter_a=['CODE_DEPT', 'NOM_DEPT'],
    field_name_filter_b=['AREA', 'DENSITY'],
    rename_output_field_from_geolayer_a={'CODE_DEPT': 'id', 'NOM_DEPT': 'name'},
    rename_output_field_from_geolayer_b={'AREA': 'area', 'DENSITY': 'density'},
    geometry_ref='geolayer_a'
)

print(geoformat.print_features_data_table(geolayer_right_join))

# >>>
# +--------+----+---------+---------+---------+---------+--------------------------------+
# | i_feat | id | name    | area    | density | type    | coordinates                    |
# +========+====+=========+=========+=========+=========+================================+
# | 0      | None| None    | 5549.31 | 67.47   | None    | None                           |
# | 1      | 53 | MAYENNE | 5208.37 | 59.03   | Polygon | [[[399495.0, 6830885.0] ...]]] |
# | 2      | 02 | AISNE   | 7418.97 | 72.04   | Polygon | [[[776081.0, 6923412.0] ...]]] |
# | 3      | 02 | AISNE   | 7418.97 | 72.04   | Polygon | [[[776081.0, 6923412.0] ...]]] |
# +--------+----+---------+---------+---------+---------+--------------------------------+
```

#### Clause functions

Similar to SQL language, the purpose of clauses is to find, sort, and group data within a geolayer.
Each function returns a list of feature identifiers corresponding to what the user is looking for. 
From the result, with the function `create_geolayer_from_i_feat_list`, a new geolayer can be reconstructed.

##### clause where

The `clause_where` function returns feature identifiers corresponding to the desired value of a field according to a given predicate.

Here is the list of predicates managed by the function:
* `=`
* `<`
* `>`
* `<>`
* `LIKE`
* `BETWEEN`
* `IS`
* `IS NOT`


```python
import geoformat

from tests.data.geolayers import geolayer_fr_dept_data_only

i_feat_list = geoformat.clause_where(geolayer_fr_dept_data_only, 'NOM_DEPT', '=', 'MEUSE')

print(i_feat_list)

meuse_geolayer = geoformat.create_geolayer_from_i_feat_list(geolayer_fr_dept_data_only, i_feat_list)

print(geoformat.print_features_data_table(meuse_geolayer))

# >>> [15]
# >>>
# +--------+-----------+----------+
# | i_feat | CODE_DEPT | NOM_DEPT |
# +========+===========+==========+
# | 0      | 55        | MEUSE    |
# +--------+-----------+----------+
```
##### clause group by

The `clause_group_by` clause is used to highlight the unique occurrences of one or more fields in a geolayer.

In return, the function returns a dictionary with a tuple of unique values as the key and a list of feature identifiers as the value.

```python
import geoformat

from tests.data.geolayers import geolayer_fr_dept_population

clause_group_by_dict = geoformat.clause_group_by(geolayer_fr_dept_population, 'INSEE_REG')

print(clause_group_by_dict)

for insee_reg_value, i_feat_list in clause_group_by_dict.items():
    insee_reg_geolayer =  geoformat.create_geolayer_from_i_feat_list(geolayer_fr_dept_population, i_feat_list)
    print(geoformat.print_features_data_table(insee_reg_geolayer))

# >>> {('76',): [0, 8, 28, 31, 36, 40, 42, 47, 48, 57, 77, 79, 92], ('75',): [1, 13, 16, 22, 25, 26, 32, 56, 64, 75, 83, 87], ('84',): [2, 6, 20, 30, 35, 44, 55, 66, 74, 76, 78, 80], ('32',): [3, 21, 46, 59, 67], ('44',): [4, 5, 15, 18, 24, 39, 41, 45, 54, 58], ('93',): [7, 49, 82, 84, 89, 93], ('27',): [9, 14, 27, 34, 60, 62, 69, 72], ('52',): [10, 29, 50, 61, 88], ('11',): [11, 43, 68, 71, 90, 91, 94, 95], ('28',): [12, 17, 37, 38, 70], ('24',): [19, 23, 33, 53, 81, 85], ('53',): [51, 63, 65, 73], ('94',): [52, 86]}
# >>>
# +--------+-----------+-----------+------------+---------+---------+
# | i_feat | CODE_DEPT | INSEE_REG | POPULATION | AREA    | DENSITY |
# +========+===========+===========+============+=========+=========+
# | 0      | 32        | 76        | 191091     | 6304.33 | 30.31   |
# | 1      | 31        | 76        | 1362672    | 6364.82 | 214.09  |
# | 2      | 82        | 76        | 258349     | 3731.0  | 69.24   |
# | 3      | 12        | 76        | 279206     | 8770.69 | 31.83   |
# | 4      | 81        | 76        | 387890     | 5785.79 | 67.04   |
# | 5      | 30        | 76        | 744178     | 5874.71 | 126.67  |
# | 6      | 11        | 76        | 370260     | 6351.35 | 58.3    |
# | 7      | 46        | 76        | 173828     | 5221.64 | 33.29   |
# | 8      | 65        | 76        | 228530     | 4527.89 | 50.47   |
# | 9      | 09        | 76        | 153153     | 4921.75 | 31.12   |
# | 10     | 34        | 76        | 1144892    | 6231.05 | 183.74  |
# | 11     | 66        | 76        | 474452     | 4147.76 | 114.39  |
# | 12     | 48        | 76        | 76601      | 5172.02 | 14.81   |
# +--------+-----------+-----------+------------+---------+---------+
# >>>
# +--------+-----------+-----------+------------+----------+---------+
# | i_feat | CODE_DEPT | INSEE_REG | POPULATION | AREA     | DENSITY |
# +========+===========+===========+============+==========+=========+
# | 0      | 87        | 75        | 374426     | 5549.31  | 67.47   |
# | 1      | 16        | 75        | 352335     | 5963.54  | 59.08   |
# | 2      | 33        | 75        | 1583384    | 10068.74 | 157.26  |
# | 3      | 64        | 75        | 677309     | 7691.6   | 88.06   |
# | 4      | 86        | 75        | 436876     | 7025.24  | 62.19   |
# | 5      | 24        | 75        | 413606     | 9209.9   | 44.91   |
# | 6      | 23        | 75        | 118638     | 5589.16  | 21.23   |
# | 7      | 19        | 75        | 241464     | 5888.93  | 41.0    |
# | 8      | 40        | 75        | 407444     | 9353.03  | 43.56   |
# | 9      | 17        | 75        | 644303     | 6913.03  | 93.2    |
# | 10     | 79        | 75        | 374351     | 6029.06  | 62.09   |
# | 11     | 87        | 75        | 374426     | 5549.31  | 67.47   |
# +--------+-----------+-----------+------------+----------+---------+
# >>>
# +--------+-----------+-----------+------------+---------+---------+
# | i_feat | CODE_DEPT | INSEE_REG | POPULATION | AREA    | DENSITY |
# +========+===========+===========+============+=========+=========+
# | 0      | 38        | 84        | 1258722    | 7868.79 | 159.96  |
# | 1      | 42        | 84        | 762941     | 4795.85 | 159.08  |
# | 2      | 07        | 84        | 325712     | 5562.05 | 58.56   |
# | 3      | 69        | 84        | 1843319    | 3253.11 | 566.63  |
# | 4      | 63        | 84        | 653742     | 8003.1  | 81.69   |
# | 5      | 43        | 84        | 227283     | 4996.58 | 45.49   |
# | 6      | 01        | 84        | 643350     | 5773.77 | 111.43  |
# | 7      | 74        | 84        | 807360     | 4596.53 | 175.65  |
# | 8      | 03        | 84        | 337988     | 7365.26 | 45.89   |
# | 9      | 15        | 84        | 145143     | 5767.47 | 25.17   |
# | 10     | 26        | 84        | 511553     | 6553.53 | 78.06   |
# | 11     | 73        | 84        | 431174     | 6260.4  | 68.87   |
# +--------+-----------+-----------+------------+---------+---------+
# >>>
# +--------+-----------+-----------+------------+---------+---------+
# | i_feat | CODE_DEPT | INSEE_REG | POPULATION | AREA    | DENSITY |
# +========+===========+===========+============+=========+=========+
# | 0      | 62        | 32        | 1468018    | 6714.14 | 218.65  |
# | 1      | 02        | 32        | 534490     | 7418.97 | 72.04   |
# | 2      | 80        | 32        | 572443     | 6206.58 | 92.23   |
# | 3      | 59        | 32        | 2604361    | 5774.99 | 450.97  |
# | 4      | 60        | 32        | 824503     | 5893.6  | 139.9   |
# +--------+-----------+-----------+------------+---------+---------+
# >>>
# +--------+-----------+-----------+------------+---------+---------+
# | i_feat | CODE_DEPT | INSEE_REG | POPULATION | AREA    | DENSITY |
# +========+===========+===========+============+=========+=========+
# | 0      | 08        | 44        | 273579     | 5253.13 | 52.08   |
# | 1      | 10        | 44        | 310020     | 6021.83 | 51.48   |
# | 2      | 55        | 44        | 187187     | 6233.18 | 30.03   |
# | 3      | 88        | 44        | 367673     | 5891.56 | 62.41   |
# | 4      | 57        | 44        | 1043522    | 6252.63 | 166.89  |
# | 5      | 52        | 44        | 175640     | 6249.91 | 28.1    |
# | 6      | 67        | 44        | 1125559    | 4796.37 | 234.67  |
# | 7      | 51        | 44        | 568895     | 8195.78 | 69.41   |
# | 8      | 54        | 44        | 733481     | 5283.29 | 138.83  |
# | 9      | 68        | 44        | 764030     | 3526.37 | 216.66  |
# +--------+-----------+-----------+------------+---------+---------+
# >>>
# +--------+-----------+-----------+------------+---------+---------+
# | i_feat | CODE_DEPT | INSEE_REG | POPULATION | AREA    | DENSITY |
# +========+===========+===========+============+=========+=========+
# | 0      | 06        | 93        | 1083310    | 4291.62 | 252.42  |
# | 1      | 04        | 93        | 163915     | 6993.79 | 23.44   |
# | 2      | 05        | 93        | 141284     | 5685.31 | 24.85   |
# | 3      | 84        | 93        | 559479     | 3577.19 | 156.4   |
# | 4      | 83        | 93        | 1058740    | 6002.84 | 176.37  |
# | 5      | 13        | 93        | 2024162    | 5082.57 | 398.26  |
# +--------+-----------+-----------+------------+---------+---------+
# >>>
# +--------+-----------+-----------+------------+---------+---------+
# | i_feat | CODE_DEPT | INSEE_REG | POPULATION | AREA    | DENSITY |
# +========+===========+===========+============+=========+=========+
# | 0      | 71        | 27        | 553595     | 8598.33 | 64.38   |
# | 1      | 25        | 27        | 539067     | 5248.31 | 102.71  |
# | 2      | 39        | 27        | 260188     | 5040.63 | 51.62   |
# | 3      | 70        | 27        | 236659     | 5382.37 | 43.97   |
# | 4      | 90        | 27        | 142622     | 609.64  | 233.94  |
# | 5      | 89        | 27        | 338291     | 7450.97 | 45.4    |
# | 6      | 58        | 27        | 207182     | 6862.87 | 30.19   |
# | 7      | 21        | 27        | 532871     | 8787.51 | 60.64   |
# +--------+-----------+-----------+------------+---------+---------+
# >>>
# +--------+-----------+-----------+------------+---------+---------+
# | i_feat | CODE_DEPT | INSEE_REG | POPULATION | AREA    | DENSITY |
# +========+===========+===========+============+=========+=========+
# | 0      | 53        | 52        | 307445     | 5208.37 | 59.03   |
# | 1      | 49        | 52        | 813493     | 7161.34 | 113.6   |
# | 2      | 72        | 52        | 566506     | 6236.75 | 90.83   |
# | 3      | 44        | 52        | 1394909    | 6992.78 | 199.48  |
# | 4      | 85        | 52        | 675247     | 6758.23 | 99.91   |
# +--------+-----------+-----------+------------+---------+---------+
# >>>
# +--------+-----------+-----------+------------+---------+----------+
# | i_feat | CODE_DEPT | INSEE_REG | POPULATION | AREA    | DENSITY  |
# +========+===========+===========+============+=========+==========+
# | 0      | 78        | 11        | 1438266    | 2305.64 | 623.8    |
# | 1      | 77        | 11        | 1403997    | 5924.64 | 236.98   |
# | 2      | 95        | 11        | 1228618    | 1254.18 | 979.62   |
# | 3      | 91        | 11        | 1296130    | 1818.35 | 712.81   |
# | 4      | 94        | 11        | 1387926    | 244.7   | 5671.95  |
# | 5      | 92        | 11        | 1609306    | 175.63  | 9163.05  |
# | 6      | 93        | 11        | 1623111    | 236.96  | 6849.73  |
# | 7      | 75        | 11        | 2187526    | 105.44  | 20746.64 |
# +--------+-----------+-----------+------------+---------+----------+
# >>>
# +--------+-----------+-----------+------------+---------+---------+
# | i_feat | CODE_DEPT | INSEE_REG | POPULATION | AREA    | DENSITY |
# +========+===========+===========+============+=========+=========+
# | 0      | 50        | 28        | 496883     | 6015.07 | 82.61   |
# | 1      | 14        | 28        | 694002     | 5588.48 | 124.18  |
# | 2      | 27        | 28        | 601843     | 6035.85 | 99.71   |
# | 3      | 76        | 28        | 1254378    | 6318.26 | 198.53  |
# | 4      | 61        | 28        | 283372     | 6142.73 | 46.13   |
# +--------+-----------+-----------+------------+---------+---------+
# >>>
# +--------+-----------+-----------+------------+---------+---------+
# | i_feat | CODE_DEPT | INSEE_REG | POPULATION | AREA    | DENSITY |
# +========+===========+===========+============+=========+=========+
# | 0      | 18        | 24        | 304256     | 7292.67 | 41.72   |
# | 1      | 41        | 24        | 331915     | 6412.3  | 51.76   |
# | 2      | 45        | 24        | 678008     | 6804.01 | 99.65   |
# | 3      | 28        | 24        | 433233     | 5927.23 | 73.09   |
# | 4      | 37        | 24        | 606511     | 6147.6  | 98.66   |
# | 5      | 36        | 24        | 222232     | 6887.38 | 32.27   |
# +--------+-----------+-----------+------------+---------+---------+
# >>>
# +--------+-----------+-----------+------------+---------+---------+
# | i_feat | CODE_DEPT | INSEE_REG | POPULATION | AREA    | DENSITY |
# +========+===========+===========+============+=========+=========+
# | 0      | 56        | 53        | 750863     | 6864.07 | 109.39  |
# | 1      | 35        | 53        | 1060199    | 6830.2  | 155.22  |
# | 2      | 29        | 53        | 909028     | 6756.76 | 134.54  |
# | 3      | 22        | 53        | 598814     | 6963.26 | 86.0    |
# +--------+-----------+-----------+------------+---------+---------+
# >>>
# +--------+-----------+-----------+------------+---------+---------+
# | i_feat | CODE_DEPT | INSEE_REG | POPULATION | AREA    | DENSITY |
# +========+===========+===========+============+=========+=========+
# | 0      | 2A        | 94        | 157249     | 4028.53 | 39.03   |
# | 1      | 2B        | 94        | 177689     | 4719.71 | 37.65   |
# +--------+-----------+-----------+------------+---------+---------+
```

##### clause order by

The clause_order_by function returns a list of geolayer feature identifiers ordered according to the values contained in one or more fields in ascending (ASC) or descending (DESC) order.

```python
import geoformat
from tests.data.geolayers import geolayer_france_japan

order_i_feat_list = geoformat.clause_order_by(geolayer_france_japan, [['country', 'ASC'], ['name', 'DESC']])

print(order_i_feat_list)

geolayer_france_japan_order = geoformat.create_geolayer_from_i_feat_list(geolayer_france_japan, order_i_feat_list)

print(geoformat.print_features_data_table(geolayer_france_japan_order))

# >>> [0, 2, 4, 1, 3, 5]
# >>>
# +--------+-------------+---------+------------+--------------------------------+
# | i_feat | name        | country | type       | coordinates                    |
# +========+=============+=========+============+================================+
# | 0      | Paris       | France  | Point      | [2.34886039, 48.85332408]      |
# | 1      | Loire       | France  | LineString | [[-2.13684082, 47.282955 ...]] |
# | 2      | France      | France  | Polygon    | [[[2.4609375, 51.124212 ...]]] |
# | 3      | Tokyo       | Japan   | Point      | [139.75309029, 35.68537297]    |
# | 4      | Katsuragawa | Japan   | LineString | [[135.42228699, 34.68291 ...]] |
# | 5      | Honshu      | Japan   | Polygon    | [[[140.88867188, 41.525 ...]]] |
# +--------+-------------+---------+------------+--------------------------------+
```

#### Field statistics
As its name suggests, `field_statistics` is a function for producing statistics on one or more fields. Among other things, it can be used to characterize the statistical distribution of one or more fields in a geolayer.

Here are the different indicators that can be calculated:

- `SUM`
- `MEAN`
- `MIN`
- `MAX`
- `RANGE`
- `STD`
- `COUNT`
- `FIRST`
- `LAST`
- `VARIANCE`
- `ALL`

This function returns a dictionary made up of field names as keys, which returns a dictionary where the key is the indicator and the value is the statistical result.

```python
import geoformat

from tests.data.geolayers import geolayer_fr_dept_population

dept_population_stat = geoformat.field_statistics(geolayer_fr_dept_population, [['POPULATION', 'SUM'], ['POPULATION', 'MIN'], ['POPULATION', 'MAX']])

print(dept_population_stat)

# >>> {'POPULATION': {'SUM': 64638088, 'MIN': 76601, 'MAX': 2604361}}
```
### Feature usefully functions

* [Update attributes in feature](#update-attributes-in-feature)
  * [Drop field](#drop-field)
  * [Drop field that not exists](#drop-field-that-not-exists)
* [Rename field](#rename-field)
* [Merge feature](#merge-feature)
* [Feature filter](#feature-filter)

#### Update attributes in feature

##### Drop field

If your feature contains attributes, then it is possible to delete a field containing data with `drop_field_in_feature`.

```python
import geoformat

feature = {"attributes": {"CODE_DEPT": "53", "NOM_DEPT": "MAYENNE"}}

feature_drop_field = geoformat.drop_field_in_feature(feature, "NOM_DEPT")

print(feature_drop_field)

# >>> {"attributes": {"CODE_DEPT": "53"}}
```

##### Drop field that not exists


Suppose we have a "feature" containing attributes, and we only want to keep certain fields. That's what `drop_field_that_not_exists_in_feature` is for. 
It's the exact opposite of the `drop_field_in_feature` function.

```python
import geoformat

feature = {"attributes": {"CODE_DEPT": "53", "NOM_DEPT": "MAYENNE"}}

feature_drop_field = geoformat.drop_field_that_not_exists_in_feature(feature, "NOM_DEPT")

print(feature_drop_field)

# >>> {"attributes": {"NOM_DEPT": "MAYENNE"}}
```

#### Rename field

You can change the name of a field contained in a feature using the `rename_field_in_feature` function.

```python
import geoformat

feature = {"attributes": {"CODE_DEPT": "53", "NOM_DEPT": "MAYENNE"}}

feature_drop_field = geoformat.rename_field_in_feature(feature, "CODE_DEPT", "ID")

print(feature_drop_field)

# >>> {"attributes": {"ID": "53", "NOM_DEPT": "MAYENNE"}}
```


#### Merge feature

With `merge_feature`, you can merge two features into one. 
Of course, there are options for easily merging two features:
- `merge_metadata`: You can add geolayer metadata. They are used as constraints in the merge to check that the output feature conforms to an insertion in the geolayer from which the metadata came.
- `field_name_filter_a`: list of fields from feature_a that you want to keep in the output feature.
- `field_name_filter_b`: list of fields from feature_b that you want to keep in the output feature.
- `rename_fields_a`: you can rename fields to avoid field name collisions when merging. Here you can rename fields from feature_a.
- `rename_fields_b`: you can rename fields to avoid field name collisions when merging. Here you can rename fields from feature_b.
- `geometry_ref`: a feature can contain only one geometry, so here you have to choose which feature geometry to keep.
  (default value: `feature_a`)

Examples:


```python
import geoformat

feature_a = {"attributes": {"CODE_DEPT": "53", "NOM_DEPT": "MAYENNE"}}
feature_b = {
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [399495.0, 6830885.0],
                [400197.0, 6773697.0],
                [393110.0, 6750366.0],
                [440863.0, 6746201.0],
                [455060.0, 6767070.0],
                [465298.0, 6799724.0],
                [463434.0, 6833996.0],
                [429868.0, 6822252.0],
                [399495.0, 6830885.0],
            ]
        ],
    }
}

feature_merged = geoformat.merge_feature(feature_a, feature_b, geometry_ref='feature_b')

print(feature_merged)

# >>> {'attributes': {'CODE_DEPT': '53', 'NOM_DEPT': 'MAYENNE'}, 'geometry': {'type': 'Polygon', 'coordinates': [[[399495.0, 6830885.0], [400197.0, 6773697.0], [393110.0, 6750366.0], [440863.0, 6746201.0], [455060.0, 6767070.0], [465298.0, 6799724.0], [463434.0, 6833996.0], [429868.0, 6822252.0], [399495.0, 6830885.0]]]}}
```

```python
import geoformat

feature_a = {"attributes": {"CODE_DEPT": "53", "NOM_DEPT": "MAYENNE"}}
feature_b = {
    "attributes": {"CODE_DEPT": "02", "INSEE_REG": "32", "POPULATION": 534490, "AREA": 7418.97, "DENSITY": 72.04},
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [399495.0, 6830885.0],
                [400197.0, 6773697.0],
                [393110.0, 6750366.0],
                [440863.0, 6746201.0],
                [455060.0, 6767070.0],
                [465298.0, 6799724.0],
                [463434.0, 6833996.0],
                [429868.0, 6822252.0],
                [399495.0, 6830885.0],
            ]
        ],
    }
}

feature_merged = geoformat.merge_feature(feature_a, feature_b, field_name_filter_b=['POPULATION', 'AREA'], geometry_ref='feature_b')

print(feature_merged)

# >>> {'attributes': {'CODE_DEPT': '53', 'NOM_DEPT': 'MAYENNE', 'POPULATION': 534490, 'AREA': 7418.97}, 'geometry': {'type': 'Polygon', 'coordinates': [[[399495.0, 6830885.0], [400197.0, 6773697.0], [393110.0, 6750366.0], [440863.0, 6746201.0], [455060.0, 6767070.0], [465298.0, 6799724.0], [463434.0, 6833996.0], [429868.0, 6822252.0], [399495.0, 6830885.0]]]}}
```
#### Feature filter

When you want to filter out certain elements in a feature, the `feature_filter` function is for you.

It allows you to filter:
- `field_name_filter`: filter a field (or a list of fields).
- `geometry_type_filter`: filter a geometry type (if the geometry is not compatible with the desired geometry, the function returns None). You can use a list of geometries to filter.
- `bbox_filter`: filter by bbox (if the feature does not intersect the given bbox, the function returns None). You can use a list of bboxes.

Example: field filter

```python
import geoformat

feature = {'attributes': {'CODE_DEPT': '53', 'NOM_DEPT': 'MAYENNE', 'POPULATION': 534490, 'AREA': 7418.97}, 'geometry': {'type': 'Polygon', 'coordinates': [[[399495.0, 6830885.0], [400197.0, 6773697.0], [393110.0, 6750366.0], [440863.0, 6746201.0], [455060.0, 6767070.0], [465298.0, 6799724.0], [463434.0, 6833996.0], [429868.0, 6822252.0], [399495.0, 6830885.0]]]}}

filtered_feature = geoformat.feature_filter(feature, field_name_filter=['CODE_DEPT', 'NOM_DEPT'])

print(filtered_feature)

# >>> {'attributes': {'CODE_DEPT': '53', 'NOM_DEPT': 'MAYENNE'}, 'geometry': {'type': 'Polygon', 'coordinates': [[[399495.0, 6830885.0], [400197.0, 6773697.0], [393110.0, 6750366.0], [440863.0, 6746201.0], [455060.0, 6767070.0], [465298.0, 6799724.0], [463434.0, 6833996.0], [429868.0, 6822252.0], [399495.0, 6830885.0]]]}}
```

Example : geometry type filter

```python
import geoformat

feature = {'attributes': {'CODE_DEPT': '53', 'NOM_DEPT': 'MAYENNE', 'POPULATION': 534490, 'AREA': 7418.97}, 'geometry': {'type': 'Polygon', 'coordinates': [[[399495.0, 6830885.0], [400197.0, 6773697.0], [393110.0, 6750366.0], [440863.0, 6746201.0], [455060.0, 6767070.0], [465298.0, 6799724.0], [463434.0, 6833996.0], [429868.0, 6822252.0], [399495.0, 6830885.0]]]}}

filtered_feature = geoformat.feature_filter(feature, geometry_type_filter='Point' )

print(filtered_feature)

# >>> None
```

Example : multi geometry type 

```python
import geoformat

feature = {'attributes': {'CODE_DEPT': '53', 'NOM_DEPT': 'MAYENNE', 'POPULATION': 534490, 'AREA': 7418.97}, 'geometry': {'type': 'Polygon', 'coordinates': [[[399495.0, 6830885.0], [400197.0, 6773697.0], [393110.0, 6750366.0], [440863.0, 6746201.0], [455060.0, 6767070.0], [465298.0, 6799724.0], [463434.0, 6833996.0], [429868.0, 6822252.0], [399495.0, 6830885.0]]]}}

filtered_feature = geoformat.feature_filter(feature, geometry_type_filter={'Point', 'Polygon'} )

print(filtered_feature)

# >>> {'attributes': {'CODE_DEPT': '53', 'NOM_DEPT': 'MAYENNE', 'POPULATION': 534490, 'AREA': 7418.97}, 'geometry': {'type': 'Polygon', 'coordinates': [[[399495.0, 6830885.0], [400197.0, 6773697.0], [393110.0, 6750366.0], [440863.0, 6746201.0], [455060.0, 6767070.0], [465298.0, 6799724.0], [463434.0, 6833996.0], [429868.0, 6822252.0], [399495.0, 6830885.0]]]}}
```


Example : bbox filter

```python
import geoformat

feature = {'attributes': {'CODE_DEPT': '53', 'NOM_DEPT': 'MAYENNE', 'POPULATION': 534490, 'AREA': 7418.97}, 'geometry': {'type': 'Polygon', 'coordinates': [[[399495.0, 6830885.0], [400197.0, 6773697.0], [393110.0, 6750366.0], [440863.0, 6746201.0], [455060.0, 6767070.0], [465298.0, 6799724.0], [463434.0, 6833996.0], [429868.0, 6822252.0], [399495.0, 6830885.0]]]}}

filtered_feature = geoformat.feature_filter(feature, bbox_filter=(-10, -10, 10, 10) )

print(filtered_feature)

# >>> None
```


Example : list of bbox filter

```python
import geoformat

feature = {'attributes': {'CODE_DEPT': '53', 'NOM_DEPT': 'MAYENNE', 'POPULATION': 534490, 'AREA': 7418.97}, 'geometry': {'type': 'Polygon', 'coordinates': [[[399495.0, 6830885.0], [400197.0, 6773697.0], [393110.0, 6750366.0], [440863.0, 6746201.0], [455060.0, 6767070.0], [465298.0, 6799724.0], [463434.0, 6833996.0], [429868.0, 6822252.0], [399495.0, 6830885.0]]]}}

filtered_feature = geoformat.feature_filter(feature, bbox_filter=[(-10, -10, 10, 10), (392000, 6740000, 465000, 6832000) ])

print(filtered_feature)

# >>> {'attributes': {'CODE_DEPT': '53', 'NOM_DEPT': 'MAYENNE', 'POPULATION': 534490, 'AREA': 7418.97}, 'geometry': {'type': 'Polygon', 'coordinates': [[[399495.0, 6830885.0], [400197.0, 6773697.0], [393110.0, 6750366.0], [440863.0, 6746201.0], [455060.0, 6767070.0], [465298.0, 6799724.0], [463434.0, 6833996.0], [429868.0, 6822252.0], [399495.0, 6830885.0]]]}}
```

### Geolayer usefully functions

* [Create geolayer from another](#create-geolayer-from-another)
* [Primary key](#primary-key)
* [Create field](#create-field)
* [Rename field](#rename-field-1)
* [Drop field](#drop-field-1)
* [Delete feature](#delete-feature)
* [Union geolayer](#union-geolayer)
* [Geolayer geometry update](#geolayer-geometry-update)
  * [multi_geometry_to_single_geometry_geolayer](#multi_geometry_to_single_geometry_geolayer)
  * [split_geolayer_by_geometry_type](#split_geolayer_by_geometry_type)

#### Create geolayer from another

Some functions (such as clauses: `clause_where`, `group_by`, `order_by`) return a list of feature identifiers (`i_feat`). 
It is then possible to recreate a new geolayer from another using the function: `create_geolayer_from_i_feat_list`.

By default, the feature identifiers (`i_feat`) are overwritten when a new geolayer is created, but it is possible to keep the old `i_feat` identifiers using the `reset_i_feat=False` option.

Other options are available: 
- `output_geolayer_name`: choose output geolayer name
- `field_name_filter`: list of fields that you want to keep in geolayer.
- `geometry_type_filter`: list of fields that you want to keep in geolayer.
- `bbox_filter`: filter geolayer feature by bbox. You can use a list of bbox.

```python
import geoformat

geolayer = geoformat.geojson_to_geolayer(path='data/doc/dept_population_extract.geojson')

print(geoformat.print_features_data_table(geolayer))

i_feat_list = [0, 2]

new_geolayer = geoformat.create_geolayer_from_i_feat_list(geolayer, i_feat_list)

print(geoformat.print_features_data_table(new_geolayer))

# >>>
# +--------+-----------+-----------+------------+---------+---------+
# | i_feat | CODE_DEPT | INSEE_REG | POPULATION | AREA    | DENSITY |
# +========+===========+===========+============+=========+=========+
# | 0      | 87        | 75        | 374426     | 5549.31 | 67.47   |
# | 1      | 53        | 52        | 307445     | 5208.37 | 59.03   |
# | 2      | 02        | 32        | 534490     | 7418.97 | 72.04   |
# +--------+-----------+-----------+------------+---------+---------+
# >>>
# +--------+-----------+-----------+------------+---------+---------+
# | i_feat | CODE_DEPT | INSEE_REG | POPULATION | AREA    | DENSITY |
# +========+===========+===========+============+=========+=========+
# | 0      | 02        | 32        | 534490     | 7418.97 | 72.04   |
# | 1      | 87        | 75        | 374426     | 5549.31 | 67.47   |
# +--------+-----------+-----------+------------+---------+---------+
```

#### Primary key

As in relational databases, it is possible to add a primary key in order to optimize the links between geolayers.
This function returns an object which must be stored in the geolayer's metadata (for future use) or, if necessary, used independently.

```python
import geoformat

geolayer = geoformat.geojson_to_geolayer(path='data/doc/dept_population_extract.geojson')

geolayer_pk = geoformat.create_pk(geolayer, 'CODE_DEPT')

print(geolayer_pk)

# >>> {'87': 0, '53': 1, '02': 2}
```

#### Create field

```python
import geoformat

geolayer = geoformat.geojson_to_geolayer(path='data/doc/dept_population_extract.geojson')

print(geoformat.print_metadata_field_table(geolayer))

geolayer = geoformat.create_field(geolayer, 'country', 'String', 100)

print(geoformat.print_metadata_field_table(geolayer))

# >>>
# +------------+---------+-------+-----------+-------+
# | field name | type    | width | precision | index |
# +============+=========+=======+===========+=======+
# | CODE_DEPT  | String  | 2     | None      | 0     |
# | INSEE_REG  | String  | 2     | None      | 1     |
# | POPULATION | Integer | None  | None      | 2     |
# | AREA       | Real    | 6     | 2         | 3     |
# | DENSITY    | Real    | 4     | 2         | 4     |
# +------------+---------+-------+-----------+-------+
# >>>
# +------------+---------+-------+-----------+-------+
# | field name | type    | width | precision | index |
# +============+=========+=======+===========+=======+
# | CODE_DEPT  | String  | 2     | None      | 0     |
# | INSEE_REG  | String  | 2     | None      | 1     |
# | POPULATION | Integer | None  | None      | 2     |
# | AREA       | Real    | 6     | 2         | 3     |
# | DENSITY    | Real    | 4     | 2         | 4     |
# | country    | String  | 100   | None      | 5     |
# +------------+---------+-------+-----------+-------+
```

#### Rename field

```python
import geoformat

geolayer = geoformat.geojson_to_geolayer(path='data/doc/dept_population_extract.geojson')

print(geoformat.print_metadata_field_table(geolayer))

geolayer = geoformat.rename_field(geolayer, 'CODE_DEPT', 'ID')

print(geoformat.print_metadata_field_table(geolayer))

# >>>
# +------------+---------+-------+-----------+-------+
# | field name | type    | width | precision | index |
# +============+=========+=======+===========+=======+
# | CODE_DEPT  | String  | 2     | None      | 0     |
# | INSEE_REG  | String  | 2     | None      | 1     |
# | POPULATION | Integer | None  | None      | 2     |
# | AREA       | Real    | 6     | 2         | 3     |
# | DENSITY    | Real    | 4     | 2         | 4     |
# +------------+---------+-------+-----------+-------+
# >>>
# +------------+---------+-------+-----------+-------+
# | field name | type    | width | precision | index |
# +============+=========+=======+===========+=======+
# | INSEE_REG  | String  | 2     | None      | 1     |
# | POPULATION | Integer | None  | None      | 2     |
# | AREA       | Real    | 6     | 2         | 3     |
# | DENSITY    | Real    | 4     | 2         | 4     |
# | ID         | String  | 2     | None      | 0     |
# +------------+---------+-------+-----------+-------+
```

#### Drop field

```python
import geoformat

geolayer = geoformat.geojson_to_geolayer(path='data/doc/dept_population_extract.geojson')

print(geoformat.print_metadata_field_table(geolayer))

geolayer = geoformat.drop_field(geolayer, 'AREA')

print(geoformat.print_metadata_field_table(geolayer))

# >>>
# +------------+---------+-------+-----------+-------+
# | field name | type    | width | precision | index |
# +============+=========+=======+===========+=======+
# | CODE_DEPT  | String  | 2     | None      | 0     |
# | INSEE_REG  | String  | 2     | None      | 1     |
# | POPULATION | Integer | None  | None      | 2     |
# | AREA       | Real    | 6     | 2         | 3     |
# | DENSITY    | Real    | 4     | 2         | 4     |
# +------------+---------+-------+-----------+-------+
# >>>
# +------------+---------+-------+-----------+-------+
# | field name | type    | width | precision | index |
# +============+=========+=======+===========+=======+
# | CODE_DEPT  | String  | 2     | None      | 0     |
# | INSEE_REG  | String  | 2     | None      | 1     |
# | POPULATION | Integer | None  | None      | 2     |
# | DENSITY    | Real    | 4     | 2         | 3     |
# +------------+---------+-------+-----------+-------+
```

#### Delete feature

As its name suggests, `delete_feature` is used to delete an entity from a geolayer.
Unfortunately, this function does not currently allow metadata to be updated. We're working on it.


```python
import geoformat

geolayer = geoformat.geojson_to_geolayer(path='data/doc/dept_population_extract.geojson')

print(geoformat.print_features_data_table(geolayer))

geolayer = geoformat.delete_feature(geolayer, 1)

print(geoformat.print_features_data_table(geolayer))

# >>>
# +--------+-----------+-----------+------------+---------+---------+
# | i_feat | CODE_DEPT | INSEE_REG | POPULATION | AREA    | DENSITY |
# +========+===========+===========+============+=========+=========+
# | 0      | 87        | 75        | 374426     | 5549.31 | 67.47   |
# | 1      | 53        | 52        | 307445     | 5208.37 | 59.03   |
# | 2      | 02        | 32        | 534490     | 7418.97 | 72.04   |
# +--------+-----------+-----------+------------+---------+---------+
# >>>
# +--------+-----------+-----------+------------+---------+---------+
# | i_feat | CODE_DEPT | INSEE_REG | POPULATION | AREA    | DENSITY |
# +========+===========+===========+============+=========+=========+
# | 0      | 87        | 75        | 374426     | 5549.31 | 67.47   |
# | 2      | 02        | 32        | 534490     | 7418.97 | 72.04   |
# +--------+-----------+-----------+------------+---------+---------+
```

#### Union geolayer

You can merge several geolayers into one by using the `union_geolayer` function.

```python
import geoformat

france_japan_cities_geolayer = geoformat.geojson_to_geolayer('data/doc/france_japan_cities.geojson')
france_japan_rivers_geolayer =  geoformat.geojson_to_geolayer('data/doc/france_japan_rivers.geojson')
france_japan_courntries_geolayer = geoformat.geojson_to_geolayer('data/doc/france_japan_countries.geojson')

geolayer = geoformat.union_geolayer(
    [france_japan_cities_geolayer, france_japan_rivers_geolayer, france_japan_courntries_geolayer],
    'france_japan'
)

print(geoformat.print_features_data_table(geolayer))

# >>>
# +--------+-------------+---------+------------+--------------------------------+
# | i_feat | name        | country | type       | coordinates                    |
# +========+=============+=========+============+================================+
# | 0      | Paris       | France  | Point      | [2.34886039, 48.85332408]      |
# | 1      | Tokyo       | Japan   | Point      | [139.75309029, 35.68537297]    |
# | 2      | Loire       | France  | LineString | [[-2.13684082, 47.282955 ...]] |
# | 3      | Katsuragawa | Japan   | LineString | [[135.42228699, 34.68291 ...]] |
# | 4      | Honshu      | Japan   | Polygon    | [[[140.88867188, 41.525 ...]]] |
# | 5      | France      | France  | Polygon    | [[[2.4609375, 51.124212 ...]]] |
# +--------+-------------+---------+------------+--------------------------------+
```

#### Geolayer geometry update

##### multi_geometry_to_single_geometry_geolayer

If you have a multi-geometry geolayer, the function `multi_geometry_to_single_geometry_geolayer` will return a geolayer with simple geometries, so the attribute data will be duplicated as many times as there are simple geometries for a multi-geometry.

```python
import geoformat

geolayer = geoformat.geojson_to_geolayer('data/doc/data_and_geometries_extract.geojson')

geolayer_single = geoformat.multi_geometry_to_single_geometry_geolayer(geolayer)

print(geoformat.print_features_data_table(geolayer_single))

# >>>
# +--------+-----------+------------+---------+--------------------------------+
# | i_feat | CODE_DEPT | NOM_DEPT   | type    | coordinates                    |
# +========+===========+============+=========+================================+
# | 0      | 53        | MAYENNE    | Polygon | [[[399495.0, 6830885.0] ...]]] |
# | 1      | 02        | AISNE      | Polygon | [[[776081.0, 6923412.0] ...]]] |
# | 2      | 95        | VAL-D'OISE | Polygon | [[[598361.0, 6887345.0] ...]]] |
# | 3      | 56        | MORBIHAN   | Polygon | [[[229520.0, 6710085.0] ...]]] |
# | 4      | 56        | MORBIHAN   | Polygon | [[[212687.0, 6770001.0] ...]]] |
# +--------+-----------+------------+---------+--------------------------------+
```

##### split_geolayer_by_geometry_type

Imagine you have a geolayer containing several types of geometries. Of these geometries, only some are of interest, or you want to make a geolayer containing only a group of such-and-such geometries and another of such-and-such others: `split_geolayer_by_geometry_type` solves this problem.

It is possible to use the key: `SPLIT_BY_GEOMETRY_TYPE` for a `GeometryCollection`. This will distribute the geometries making up the `GeometryCollection` according to the categories present in the `geometry_type_mapping` dictionary.

Example with basic geolayer:

```python
import geoformat

geolayer = geoformat.geojson_to_geolayer('data/doc/france_japan.geojson')

for output_geolayer in geoformat.split_geolayer_by_geometry_type(
        geolayer, 
        {
            "Point": "ponctual_and_reliable" ,
            "LineString": "ponctual_and_reliable" ,
            "Polygon": "surface"
        }
):
    print(output_geolayer['metadata']['name'])
    print(geoformat.print_features_data_table(output_geolayer))

# >>>
# +--------+-------------+---------+------------+--------------------------------+
# | i_feat | name        | country | type       | coordinates                    |
# +========+=============+=========+============+================================+
# | 0      | Paris       | France  | Point      | [2.34886039, 48.85332408]      |
# | 1      | Tokyo       | Japan   | Point      | [139.75309029, 35.68537297]    |
# | 2      | Loire       | France  | LineString | [[-2.13684082, 47.282955 ...]] |
# | 3      | Katsuragawa | Japan   | LineString | [[135.42228699, 34.68291 ...]] |
# +--------+-------------+---------+------------+--------------------------------+
# >>>
# +--------+--------+---------+---------+--------------------------------+
# | i_feat | name   | country | type    | coordinates                    |
# +========+========+=========+=========+================================+
# | 0      | France | France  | Polygon | [[[2.4609375, 51.124212 ...]]] |
# | 1      | Honshu | Japan   | Polygon | [[[140.88867188, 41.525 ...]]] |
# +--------+--------+---------+---------+--------------------------------+
```

Example with GeometryCollection :
```python
import geoformat

geolayer = geoformat.geojson_to_geolayer('data/doc/geometry_collection_geolayer.geojson')

for output_geolayer in geoformat.split_geolayer_by_geometry_type(
    geolayer,                                                         
    {
        "Point": "ponctual" ,
        "LineString": "reliable" ,
        "Polygon": "surface",
        "MultiPoint": "ponctual" ,
        "MultiLineString": "reliable" ,
        "MultiPolygon": "surface",
        "GeometryCollection": "SPLIT_BY_GEOMETRY_TYPE"
    }
):
    print(output_geolayer['metadata']['name'])
    print(geoformat.print_features_data_table(output_geolayer))
# 
# >>> geometry_collection_geolayer_ponctual
# >>>
# +--------+------------+--------------------------------+
# | i_feat | type       | coordinates                    |
# +========+============+================================+
# | 0      | Point      | [-115.81, 37.24]               |
# | 1      | MultiPoint | [[-155.52, 19.61], [-156 ...]] |
# +--------+------------+--------------------------------+
# 
# >>> geometry_collection_geolayer_reliable
# >>>
# +--------+-----------------+--------------------------------+
# | i_feat | type            | coordinates                    |
# +========+=================+================================+
# | 0      | LineString      | [[8.919, 44.4074], [8.92 ...]] |
# | 1      | MultiLineString | [[[3.75, 9.25], [-130.9 ...]]] |
# +--------+-----------------+--------------------------------+
# 
# >>> geometry_collection_geolayer_surface
# >>>
# +--------+--------------+--------------------------------+
# | i_feat | type         | coordinates                    |
# +========+==============+================================+
# | 0      | Polygon      | [[[2.38, 57.322], [23.1 ...]]] |
# | 1      | MultiPolygon | [[[[3.78, 9.28], [-130 ...]]]] |
# +--------+--------------+--------------------------------+
```


### Write geolayer in GIS file

* [Geoforamt GIS drivers](#geoforamt-gis-drivers)
* [Make a GIS format transormation (shapefile => geojson)](#make-a-gis-format-transormation-shapefile--geojson)

#### Geoforamt GIS drivers

#### Make a GIS format transormation (shapefile => geojson)

You can obviously convert a geolayer to a compatible OGR file format.
In this case, you put a geolayer in 'ESRI SHAPEFILE' format and create a new file in 'GEOJSON' (with reprojection because GeoJSON should be in WGS84 coordinate system).

```python
import geoformat

gares_shp_path = 'data/FRANCE_IGN/GARES_L93.shp'
gares_geojson_path =  'data/FRANCE_IGN/GARES_L93.geojson'

geolayer = geoformat.shapefile_to_geolayer(gares_shp_path, encoding='iso-8859-15')

geolayer = geoformat.reproject_geolayer(geolayer, in_crs=2154, out_crs=4326)

geoformat.geolayer_to_geojson(geolayer, gares_geojson_path, overwrite=True)

geojson_geolayer = geoformat.geojson_to_geolayer(path=gares_geojson_path)

# print 10 first features of geojson geolayer
print(geoformat.print_features_data_table(geojson_geolayer, limit=10))

# >>>
# +--------+------------+---------------+------+-----------+------------+------+---------+------------+------------+-----------+-----------+------------------+-----------------+-------+--------------------------------+
# | i_feat | code_uic   | libelle_ga    | fret | voyageurs | code_ligne | rang | pk      | x_lambert_ | y_lambert_ | x_wgs84   | y_wgs84   | commune          | departemen      | type  | coordinates                    |
# +========+============+===============+======+===========+============+======+=========+============+============+===========+===========+==================+=================+=======+================================+
# | 0      | 87471185.0 | Messac-Guipry | N    | O         | 463000     | 1.0  | 398+272 | 339653.0   | 6757878.0  | -202440.0 | 6077344.0 | Messac           | Ille-et-Vilaine | Point | [-1.8185528943432585, 47. ...] |
# | 1      | 87471029.0 | Vern          | N    | O         | 466000     | 1.0  | 50+491  | 357685.0   | 6781809.0  | -177731.0 | 6114673.0 | Vern-sur-Seiche  | Ille-et-Vilaine | Point | [-1.5965909351293788, 48. ...] |
# | 2      | 87476317.0 | Quimperlé     | O    | O         | 470000     | 1.0  | 639+694 | 210637.0   | 6772419.0  | -395516.0 | 6085140.0 | Quimperlé        | Finistère       | Point | [-3.552988951324049, 47.8 ...] |
# | 3      | 87474031.0 | Hanvec        | N    | N         | 470000     | 1.0  | 740+360 | 171994.0   | 6828441.0  | -460348.0 | 6163846.0 | Hanvec           | Finistère       | Point | [-4.135378530070003, 48.3 ...] |
# | 4      | 87476671.0 | Questembert   | O    | O         | 470000     | 1.0  | 540+326 | 291464.0   | 6745525.0  | -272690.0 | 6054309.0 | Questembert      | Morbihan        | Point | [-2.4496209535332447, 47. ...] |
# | 5      | 87476648.0 | Ste-Anne      | N    | O         | 470000     | 1.0  | 581+996 | 253190.0   | 6747773.0  | -329570.0 | 6053535.0 | Pluneret         | Morbihan        | Point | [-2.960580973370048, 47.6 ...] |
# | 6      | 87471243.0 | St-Méen       | O    | N         | 472000     | 1.0  | 68+200  | 315077.0   | 6800114.0  | -243043.0 | 6138128.0 | St-Méen-le-Grand | Ille-et-Vilaine | Point | [-2.1832958937261893, 48. ...] |
# | 7      | 87476200.0 | Auray         | O    | O         | 473000     | 1.0  | 584+946 | 250286.0   | 6748188.0  | -333913.0 | 6053823.0 | Auray            | Morbihan        | Point | [-2.99959548260269, 47.68 ...] |
# | 8      | 87476408.0 | Belz-Ploemel  | N    | O         | 473000     | 1.0  | 591+597 | 244616.0   | 6745536.0  | -341998.0 | 6049244.0 | Ploemel          | Morbihan        | Point | [-3.072226071667076, 47.6 ...] |
# | 9      | 87473330.0 | Quintin       | O    | O         | 475000     | 1.0  | 492+810 | 264298.0   | 6827046.0  | -321902.0 | 6173216.0 | St-Brandan       | Côte-d'Armor    | Point | [-2.8917008446444417, 48. ...] |
# +--------+------------+---------------+------+-----------+------------+------+---------+------------+------------+-----------+-----------+------------------+-----------------+-------+--------------------------------+
```



## Geoformat technical description

> This section is in work in progress mode

To be used optimally, it is necessary to understand how two objects specific to Geoformat work: 
- the `Geolayer`
- the `Feature`

To sum up, the Geolayer stores Features. So, the Geolayer contains Features that contain information (attribute and/or geometric).

We'll now take a look at the technical details of how to create, modify, and manipulate these two types of objects.

### Geolayer structure

A Geolayer is the database equivalent of an attribute table.
It stores features (see below) that contain attribute data and/or geographic information.

For the moment, a geolayer is a Python dictionary.  
Some developments are underway to make it a Python object easier to manipulate.


#### How is organised a geolayer 

[//]: # (![Strucutre of Geoformat]&#40;https://framagit.org/Guilhain/Geoformat/raw/geometry_translator/images/geoformat.png&#41;)

The figure shows two branches: 
- `metadata`: stores a summary of the information characterizing the `Geolayer`. This includes its name, the fields containing attribute information, the type of geometry contained in the Geolayer, and the associated projection or coordinate system...
- `features`: stores, in dictionary form, the features that make up the `Geolayer`.


#### Geolayer metadata

The `metadata` key in the geolayer root structure is used to inform the structure of the geolayer.

If the geolayer contains attribute data, the "fields" key must be filled in.
If the geolayer contains geometries data, the "geometry_ref" key must be filled in.


##### Field type

Each field in the geolayer must be filled in the "metadata" => "fields" structure.

It is informed: 
- field name
    - field type (mandatory)
    - field width (if necessary)
    - field precision (if necessary)
    - field index (optional)

        
        | type          | width    | precision | index    |
        +===============+==========+===========+==========+
        | 'Integer'     | None     | None      | Optional |
        | 'IntegerList' | None     | None      | Optional |
        | 'Real'        | Required | Required  | Optional |
        | 'RealList'    | Required | Required  | Optional |
        | 'String'      | Required | None      | Optional |
        | 'StringList'  | Required | None      | Optional |
        | 'Binary'      | None     | None      | Optional |
        | 'Date'        | None     | None      | Optional |
        | 'Time'        | None     | None      | Optional |
        | 'DateTime'    | None     | None      | Optional |
        | 'Boolean'     | None     | None      | Optional |

##### Geometry type

Each geometry in the geolayer must be filled in the "metadata" => "geometry_ref" structure.

It is informed: 
- type: each geometry type code present in the geolayer (see table below)
- crs: coordinate reference system in WKT format or EPSG

List of valid geometries:

| Code | Name               |
|------|--------------------|
| 0    | Unknown            |
| 1    | Point              |
| 2    | LineString         |
| 3    | Polygon            |
| 4    | MultiPoint         |
| 5    | MultiLinestring    |
| 6    | MultiPolygon       |
| 7    | GeometryCollection |
| 100  | None               |

### Feature structure

The feature is the basic object that contains information.
This information is of two types: 
- attributes: alphanumeric data that describes feature
- geometry: type and coordinates that describe geometrically the feature

#### Attributes

#### Geometry

There are seven types of geometries that we can group into 3 categories.

### Attributes

### Geometries

#### 7 geometries

#### Low-level geometric objects

##### Vertex

##### Segment

##### Bbox

##### Line

##### Basics


| type         | representation                                                                                                     | sample data         | geoformat                                                                                                                                                                                                                      |
|--------------|--------------------------------------------------------------------------------------------------------------------|---------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| *Point*      | ![Point](https://framagit.org/Guilhain/Geoformat/raw/geometry_translator/images/51px-SFA_Point.svg.png)            | underground station | <pre lang="python">{<br>  "type": "Point",<br>  "coordinates": [-115.81, 37.24],<br>  'bbox': (-115.81, 37.24, -115.81, 37.24)<br>}</pre>                                                                                                                            |
| *LineString* | ![LineString](https://framagit.org/Guilhain/Geoformat/raw/geometry_translator/images/51px-SFA_LineString.svg.png)  | a road              | <pre lang="python">{<br>  "type": "LineString",<br>  "coordinates": [[8.919, 44.4074], [8.923, 44.4075]],<br>  'bbox': (8.919, 44.4074, 8.923, 44.4075)<br>}</pre>                                                                                                    | 
| *Polygon*    | ![Polygon](https://framagit.org/Guilhain/Geoformat/raw/geometry_translator/images/SFA_Polygon_with_hole.svg.png)   | an island           | <pre lang="python">{<br>  "type": "Polygon",<br>  "coordinates": [[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]], [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]],<br>  'bbox': (-120.43, -20.28, 23.194, 57.322)<br>}</pre> |


##### composed

| type              | representation                                                                                            | sample data                         | geoformat                                                                                                                                                                                                                                    |
|-------------------|-----------------------------------------------------------------------------------------------------------|-------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| *MultiPoint*      | ![MultiPoint](https://framagit.org/Guilhain/Geoformat/raw/geometry_translator/images/51px-SFA_MultiPoint.svg.png)           | exits from same underground station | <pre lang="python">{<br>  "type": "MultiPoint",<br>  "coordinates": [<br>    [-155.52, 19.61],<br>    [-156.22, 20.74],<br>    [-157.97, 21.46]<br>  ],<br>  "bbox": (-157.97, 19.61, -155.52, 21.46)<br>}</pre>                                                                                  |
| *MultiLineString* | ![MultiLineString](https://framagit.org/Guilhain/Geoformat/raw/geometry_translator/images/51px-SFA_MultiLineString.svg.png) | a river with several tributaries    | <pre lang="python">{<br>  "type": "MultiLineString",<br>  "coordinates": [<br>    [[3.75, 9.25], [-130.95, 1.52]],<br>    [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]]<br>  ],<br>  "bbox": (-130.95, -34.25, 23.15, 77.95)<br>}</pre>                                                  |
| *MultiPolygon*    | ![MultiPolygon](https://framagit.org/Guilhain/Geoformat/raw/geometry_translator/images/SFA_MultiPolygon_with_hole.svg.png)  | a country with an island            | <pre lang="python">{<br>  "type": "MultiPolygon",<br>  "coordinates": [<br>    [[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]],<br>    [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]]<br>  ],<br>  "bbox": (-130.91, -34.29, 35.12, 77.91)<br>}</pre> |

##### sets

| type                 | representation                                                                                                                    | sample data                 | geoformat                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|----------------------|-----------------------------------------------------------------------------------------------------------------------------------|-----------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| *GeometryCollection* | ![GeometryCollection](https://framagit.org/Guilhain/Geoformat/raw/geometry_translator/images/51px-SFA_GeometryCollection.svg.png) | a mix of all examples above |  <pre lang="python">{<br>  "type": 'GeometryCollection',<br>  "geometries": [<br>    {<br>      "type": "Point",<br>      "coordinates": [-115.81, 37.24],<br>      'bbox': (-115.81, 37.24, -115.81, 37.24)<br>    },<br>    {<br>      "type": "LineString",<br>      "coordinates": [[8.919, 44.4074], [8.923, 44.4075]],<br>      'bbox': (8.919, 44.4074, 8.923, 44.4075)<br>    },<br>    {<br>      "type": "Polygon",<br>      "coordinates": [[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]], [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]],<br>      'bbox': (-120.43, -20.28, 23.194, 57.322)<br>    }, <br>    {<br>      'type': 'MultiPoint',<br>      'coordinates': [[-155.52, 19.61], [-156.22, 20.74], [-157.97, 21.46]],<br>      'bbox': (-157.97, 19.61, -155.52, 21.46)<br>    },<br>    {<br>      "type": 'MultiLineString',<br>      "coordinates": [[[3.75, 9.25], [-130.95, 1.52]], [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]]],<br>      'bbox': (-130.95, -34.25, 23.15, 77.95)<br>    },<br>    {<br>      'type': 'MultiPolygon', <br>      'coordinates': [[[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]], [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]]],<br>      'bbox': (-130.91, -34.29, 35.12, 77.91)<br>    }<br>  ],<br>  'bbox': (-157.97, -34.29, 35.12, 77.95)<br>}</pre> |

## Drivers

Drivers are useful for reading and writing data in a geospatial standard like Esri Shapefile, GeoJSON, PostGIS/PostgreSQL, CSV, etc.

Geoformat is progressively integrating its own drivers, but it is possible to use the GDAL/OGR library drivers.

### Geoformat driver

| driver             | read | write | read function name    | write function name   |
|--------------------|------|-------|-----------------------|-----------------------|
| Geojson            | X    | X     | geojson_to_geolayer   | geolayer_to_geojson   |
| Postgres / Postgis | NOK  | X     |                       | geolayer_to_postgres  |
| CSV                | X    | X     | csv_to_geolayer       | geolayer_to_csv       |
| esri shapefile     | X    | X     | shapefile_to_geolayer | geolayer_to_shapefile |


### OGR GDAL driver

Useful if you want to work with ESRI Shapefile or MapInfo File or GML, you can use these two functions:

| read                   | write                 |
|------------------------|-----------------------|
| ogr_layer_to_geolayer  | geolayer_to_ogr_layer |


list of maintained drivers :

| driver_name      |
|------------------|
| "ESRI SHAPEFILE" |  
| "MAPINFO FILE"   |
| "POSTGRESQL"     |
| "GML"            |
| "KML"            |           
| "XLSX"           |          
| "CSV"            |         
| "GEOJSON"        |     


## Table of contents

<!-- TOC -->
* [Welcome to Geoformat](#welcome-to-geoformat)
  * [Introduction](#introduction)
  * [Installation](#installation)
  * [Geoformat Cookbook](#geoformat-cookbook)
    * [Create geoformat objects](#create-geoformat-objects)
      * [Create a feature](#create-a-feature)
      * [Create a geolayer](#create-a-geolayer)
        * [handmade](#handmade)
        * [Using a driver](#using-a-driver)
      * [Print data geolayer](#print-data-geolayer)
        * [Print fields metadata](#print-fields-metadata)
        * [Print features data](#print-features-data)
    * [Geometry usefully functions](#geometry-usefully-functions)
      * [Area, length, distance, bbox and centroid](#area-length-distance-bbox-and-centroid)
        * [Area](#area)
        * [Length](#length)
        * [Distance](#distance)
        * [Bbox](#bbox)
        * [Centroid](#centroid)
          * [Euclidean distance](#euclidean-distance)
          * [Manhattan distance](#manhattan-distance)
      * [Reproject](#reproject-)
        * [Reproject Geometry](#reproject-geometry)
        * [Reproject Geolayer](#reproject-geolayer)
      * [Geometry formatting](#geometry-formatting)
        * [wkb_to_geometry](#wkb_to_geometry)
        * [geometry_to_wkb](#geometry_to_wkb)
        * [wkt_to_geometry](#wkt_to_geometry)
        * [geometry_to_wkt](#geometry_to_wkt)
      * [Geometrics manipulations](#geometrics-manipulations)
        * [Generalization](#generalization)
          * [Ramer-Douglas-Peucker](#ramer-douglas-peucker)
          * [Visvalimgam Whyatt](#visvalimgam-whyatt)
        * [Merging geometries](#merging-geometries)
          * [LineString merging](#linestring-merging)
          * [Geometry merging](#geometry-merging)
        * [Point on Linestring](#point-on-linestring)
        * [Force rhr](#force-rhr)
        * [Multi and single geometry](#multi-and-single-geometry)
          * [single_geometry_to_multi_geometry](#single_geometry_to_multi_geometry)
          * [multi_geometry_to_single_geometry](#multi_geometry_to_single_geometry)
      * [Low level geometrics objects](#low-level-geometrics-objects)
        * [point, segment and bbox](#point-segment-and-bbox)
          * [point_intersects_point](#point_intersects_point)
          * [point_intersects_segment](#point_intersects_segment)
          * [point_intersects_bbox](#point_intersects_bbox)
          * [segment_intersects_segment](#segment_intersects_segment)
          * [segment_intersects_bbox](#segment_intersects_bbox)
          * [bbox_intersects_bbox](#bbox_intersects_bbox)
          * [ccw_or_cw_segments](#ccw_or_cw_segments)
          * [point_position_segment](#point_position_segment)
          * [extent_bbox](#extent_bbox)
          * [bbox_union](#bbox_union)
          * [point_bbox_position](#point_bbox_position)
          * [random](#random)
        * [Line](#line)
          * [line_parameters](#line_parameters)
          * [perpendicular_line_parameters_at_point](#perpendicular_line_parameters_at_point)
          * [point_at_distance_with_line_parameters](#point_at_distance_with_line_parameters)
          * [crossing_point_from_lines_parameters](#crossing_point_from_lines_parameters)
      * [Geometry Index and Matrix](#geometry-index-and-matrix)
        * [Geometry Index](#geometry-index)
          * [Grid index](#grid-index)
        * [Geometry Matrix](#geometry-matrix)
          * [Adjacency matrix](#adjacency-matrix)
    * [Attributes usefully functions](#attributes-usefully-functions)
      * [Attributes index](#attributes-index)
      * [Join geolayer attributes](#join-geolayer-attributes)
        * [full join](#full-join)
        * [join](#join)
        * [left join](#left-join)
        * [right join](#right-join)
      * [Clause functions](#clause-functions)
        * [clause where](#clause-where)
        * [clause group by](#clause-group-by)
        * [clause order by](#clause-order-by)
      * [Field statistics](#field-statistics)
    * [Feature usefully functions](#feature-usefully-functions)
      * [Update attributes in feature](#update-attributes-in-feature)
        * [Drop field](#drop-field)
        * [Drop field that not exists](#drop-field-that-not-exists)
      * [Rename field](#rename-field)
      * [Merge feature](#merge-feature)
      * [Feature filter](#feature-filter)
    * [Geolayer usefully functions](#geolayer-usefully-functions)
      * [Create geolayer from another](#create-geolayer-from-another)
      * [Primary key](#primary-key)
      * [Create field](#create-field)
      * [Rename field](#rename-field-1)
      * [Drop field](#drop-field-1)
      * [Delete feature](#delete-feature)
      * [Union geolayer](#union-geolayer)
      * [Geolayer geometry update](#geolayer-geometry-update)
        * [multi_geometry_to_single_geometry_geolayer](#multi_geometry_to_single_geometry_geolayer)
        * [split_geolayer_by_geometry_type](#split_geolayer_by_geometry_type)
    * [Write geolayer in GIS file](#write-geolayer-in-gis-file)
      * [Geoforamt GIS drivers](#geoforamt-gis-drivers)
      * [Make a GIS format transormation (shapefile => geojson)](#make-a-gis-format-transormation-shapefile--geojson)
  * [Geoformat technical description](#geoformat-technical-description)
    * [Geolayer structure](#geolayer-structure)
      * [How is organised a geolayer](#how-is-organised-a-geolayer-)
      * [Geolayer metadata](#geolayer-metadata)
        * [Field type](#field-type)
        * [Geometry type](#geometry-type)
    * [Feature structure](#feature-structure)
      * [Attributes](#attributes)
      * [Geometry](#geometry)
    * [Attributes](#attributes-1)
    * [Geometries](#geometries)
      * [7 geometries](#7-geometries)
      * [Low-level geometric objects](#low-level-geometric-objects)
        * [Vertex](#vertex)
        * [Segment](#segment)
        * [Bbox](#bbox-1)
        * [Line](#line-1)
        * [Basics](#basics)
        * [composed](#composed)
        * [sets](#sets)
  * [Drivers](#drivers)
    * [Geoformat driver](#geoformat-driver)
    * [OGR GDAL driver](#ogr-gdal-driver)
  * [Table of contents](#table-of-contents)
<!-- TOC -->



## Publish new Geoformat version on pypi

```bash
python -m build
twine upload dist/*
```

##  Install dependencies 

```bash
pip install -e .
```

## Install GDAL

```bash
pip install gdal[numpy]=="$(gdal-config --version).*"
```