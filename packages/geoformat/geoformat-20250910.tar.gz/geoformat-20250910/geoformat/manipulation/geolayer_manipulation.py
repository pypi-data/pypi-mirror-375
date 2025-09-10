import copy

from geoformat import features_fields_type_scan, fields_scan_to_fields_metadata, features_geometry_ref_scan, \
    geometries_scan_to_geometries_metadata, feature_filter, feature_serialize, recast_field
from geoformat.conf.fields_variable import none_value_pattern
from geoformat.conf.geometry_variable import GEOFORMAT_GEOMETRY_TYPE
from geoformat.conf.error_messages import (
    field_name_not_indexing,
    key_use_only_by_geometry,
    geometry_not_in_variable,
    feature_missing
)
from geoformat.conf.format_data import value_to_iterable_value
from geoformat.conversion.fields_conversion import recast_field
from geoformat.conversion.feature_conversion import (
    feature_deserialize,
    feature_serialize,
)
from geoformat.geoprocessing.geoparameters.bbox import bbox_union
from geoformat.manipulation.feature_manipulation import (
    rename_field_in_feature,
    drop_field_in_feature,
)
from geoformat.manipulation.metadata_manipulation import (
    drop_field_in_metadata,
    rename_field_in_metadata,
    create_field_in_metadata,
    check_if_field_exists_in_metadata,
    check_attributes_index_in_metadata,
    add_attributes_index_in_metadata,
)


def delete_feature(geolayer, i_feat_to_delete):
    """Delete given i_feat feature from geolayer

    TODO add an update for geometry_ref metadata
    """
    i_feat_to_delete_list = value_to_iterable_value(
        value=i_feat_to_delete, output_iterable_type=list
    )
    for i_feat in i_feat_to_delete_list:
        if i_feat in geolayer["features"]:
            # TODO add delete (update) index (attributes and geometry) / matrix
            del geolayer["features"][i_feat]
        else:
            raise Exception(feature_missing.format(i_feat=i_feat))

    if not geolayer["features"]:
        if "fields" in geolayer["metadata"]:
            del geolayer["metadata"]["fields"]

        if "geometry_ref" in geolayer["metadata"]:
            del geolayer["metadata"]["geometry_ref"]

        if "index" in geolayer["metadata"]:
            del geolayer["metadata"]["index"]

        if "matrix" in geolayer["metadata"]:
            del geolayer["metadata"]["matrix"]

    return geolayer


def drop_field(geolayer, field_name_to_drop):
    """
    This function allow to drop a field in geolayer.

    :param geolayer: input geolayer.
    :param field_name_to_drop: field name in geolayer to drop. can be a fields list
    :return: geolayer with field drop.
    """
    field_name_to_drop = value_to_iterable_value(
        value=field_name_to_drop, output_iterable_type=list
    )
    geolayer["metadata"] = drop_field_in_metadata(
        metadata=geolayer["metadata"], field_name_or_field_name_list=field_name_to_drop
    )

    # delete field in features
    delete_i_feat_list = []
    for i_feat, feature in geolayer["features"].items():
        feature = drop_field_in_feature(
            feature=feature, field_name_or_field_name_list=field_name_to_drop
        )
        geolayer["features"][i_feat] = feature

        if not feature:
            delete_i_feat_list.append(i_feat)

    # delete feature with no data in it
    if delete_i_feat_list:
        geolayer = delete_feature(
            geolayer=geolayer, i_feat_to_delete=delete_i_feat_list
        )

    return geolayer


def rename_field(geolayer, old_field_name, new_field_name):
    """
    Rename field in geolayer

    :param geolayer: input geolayer.
    :param old_field_name: actual name of field that we want to change.
    :param new_field_name: new field's name that we want to apply.
    :return: geolayer with field rename
    """
    # rename field in metadata
    geolayer["metadata"] = rename_field_in_metadata(
        metadata=geolayer["metadata"],
        old_field_name=old_field_name,
        new_field_name=new_field_name,
    )
    # rename in features
    for i_feat, feature in geolayer["features"].items():
        feature = rename_field_in_feature(
            feature=feature,
            old_field_name=old_field_name,
            new_field_name=new_field_name,
        )
        geolayer["features"][i_feat] = feature

    return geolayer


def create_field(
    geolayer,
    field_name,
    field_type,
    field_width=None,
    field_precision=None,
    field_index=None,
):
    """
    Create new field in geolayer

    :param geolayer: input geolayer
    :param field_name: new field name
    :param field_type: field type
    :param field_width: field width
    :param field_precision: field precision
    :param field_index: field index
    :return: geolayer with new field in it
    """

    output_geolayer = copy.deepcopy(geolayer)

    new_metadata = create_field_in_metadata(
        metadata=geolayer["metadata"],
        field_name=field_name,
        field_type=field_type,
        field_width=field_width,
        field_precision=field_precision,
    )

    output_geolayer["metadata"] = new_metadata
    if new_metadata["fields"][field_name]["index"] != field_index:
        output_geolayer = recast_field(
            geolayer_to_recast=output_geolayer,
            field_name_to_recast=field_name,
            reindex=field_index,
        )

    return output_geolayer


def add_attributes_index(geolayer, field_name, index):
    """Store index in geolayer

    :param geolayer: geolayer to add an attributes
    :field_name: name of field concern by index
    :index: index that we want to add to field of geolayer
    :return: geolayer with index in it
    """

    metadata = add_attributes_index_in_metadata(
        metadata=geolayer["metadata"], field_name=field_name, index=index
    )
    geolayer["metadata"] = metadata

    return geolayer


def check_attributes_index(geolayer, field_name, type=None):
    """
    Return True or False if an attributes index in found in geolayer for input field_name optionaly we can test
    type index

    :param geolayer: input geolayer
    :param field_name: field name where is the index
    :param type: type of indexing (hashtable/btree ...)
    :return: Boolean
    """

    return check_attributes_index_in_metadata(
        metadata=geolayer["metadata"], field_name=field_name, type=type
    )


def delete_attributes_index(geolayer, field_name, type=None):
    """Delete attributes index when existing in geolayer. Opionnaly you can filter on index type

    :param geolayer: input Geolayer
    :param field_name: field name where is the index
    :param type: type of indexing (hashtable/btree ...)
    :return: Geolayer without index for given field_name (and optionally index type)
    """

    if check_attributes_index(geolayer, field_name, type) is True:
        del geolayer["metadata"]["index"]["attributes"][field_name]
        if len(geolayer["metadata"]["index"]["attributes"]) == 0:
            del geolayer["metadata"]["index"]["attributes"]
        if len(geolayer["metadata"]["index"]) == 0:
            del geolayer["metadata"]["index"]
    else:
        raise Exception(field_name_not_indexing.format(field_name=field_name))

    return geolayer


def check_if_field_exists(geolayer, field_name):
    """
    Check if field exists in given Geolayer.

    :param geolayer: input geolayer where existing field name is tested.
    :param field_name: name of field.
    :return: True if field exists False if not.
    """

    return check_if_field_exists_in_metadata(
        metadata=geolayer["metadata"], field_name=field_name
    )


def _get_driver_geometry_type_matching_i_feat_and_geometry_type_filter(
    geolayer,
    geometry_type_mapping,
):
    """
    Return a dict by geometry type fill in geometry_type_mapping variable.
    For each key is associate a list that contains dicts with features geolayer variable information in it.
        Each dict in list have this key value informations :
            i_feat : geolayer feature id
            i_geom : position of geometry in feature if SPLIT_BY_GEOMETRY_TYPE
            feature_geometry : output geometry

    SPLIT_BY_GEOMETRY_TYPE will divide a collection of geometry into geometries and distribute the geometries taking
    into account the characteristics set for each geometry in the variable: geometry_type_mapping.
    In case of EMPTY geometry collection an empty geometry is return for each type of geometry.

    TODO Usefully options that can be add further (if necessary)
    TODO SIMPLE_GEOMETRY
    TODO CONVERT_TO_POINT
    TODO CONVERT_TO_LINESTRING

    :param geolayer: input geolayer
    :param geometry_type_mapping: geometry mapping
    :return: dict described above
    """
    driver_i_feat_geometry_to_filter = {}
    geolayer_serialize = geolayer['metadata'].get("feature_serialize")
    # loop on each features
    for i_feat, feature in geolayer["features"].items():
        if geolayer_serialize is True:
            feature = feature_deserialize(feature, bbox=False)
        if feature.get("geometry"):
            geometry = feature["geometry"]
            geometry_type = geometry["type"]
            group_geometry_key = geometry_type_mapping.get(geometry_type)
            if group_geometry_key is None:
                raise Exception(geometry_not_in_variable.format(geometry_type=geometry_type, variable_name='geometry_type_mapping'))
            # put geometry(ies) in a list
            if group_geometry_key == "SPLIT_BY_GEOMETRY_TYPE":
                if 'geometries' in geometry:
                    geometry_list = geometry["geometries"]
                    if not geometry_list:  # if GEOMETRYCOLLECTION EMPTY
                        # create list with output geometry type
                        output_geometry_type_set = set()
                        output_geometry_type_list = []
                        for input_geometry, output_geometry in geometry_type_mapping.items():
                            if output_geometry not in output_geometry_type_set and output_geometry.upper() in GEOFORMAT_GEOMETRY_TYPE:
                                output_geometry_type_set.update([output_geometry])
                                output_geometry_type_list.append(output_geometry)

                        geometry_list = [{'type': geometry_type, "coordinates": []} for geometry_type in output_geometry_type_list]
                else:
                    raise Exception(key_use_only_by_geometry.format(
                        key="SPLIT_BY_GEOMETRY_TYPE",
                        geometry_type='GEOMETRYCOLLECTION'
                    ))
            else:
                geometry_list = [geometry]

            # loop on geometries
            if geometry_list:
                for i_geom, geometry_in_list in enumerate(geometry_list):
                    geometry_in_list_type = geometry_in_list["type"]
                    group_geometry_key_in_list = geometry_type_mapping[
                        geometry_in_list_type
                    ]

                    i_feat_matching_geom = {
                        "i_feat": i_feat,
                        "i_geom": i_geom,
                        "feature_geometry": geometry_in_list,
                    }
                    if driver_i_feat_geometry_to_filter.get(group_geometry_key_in_list):
                        driver_i_feat_geometry_to_filter[
                            group_geometry_key_in_list
                        ].append(i_feat_matching_geom)
                    else:
                        driver_i_feat_geometry_to_filter[group_geometry_key_in_list] = [
                            i_feat_matching_geom
                        ]
            # if no geometries
            else:
                pass

    return driver_i_feat_geometry_to_filter


def split_geolayer_by_geometry_type(
    geolayer,
    geometry_type_mapping
):
    """
    Split input geolayer according to the geometry_type_mapping variable.

    geometry_type_mapping is a dictionary witch key represents a geoformat geometry type and value represents the type
    of geometry we want to output.
    For GeometryCollection geometry type, only, you can use value SPLIT_BY_GEOMETRY_TYPE. This means that if a feature
    of the input geolayer contains a GeometryCollection in output this entity will be split according to the geometries
    contained in the GeometryCollection.

    Example of geometry_type_mapping :
    {
            "Point": "Point",
            "LineString": "LineString",
            "Polygon": "Polygon",
            "MultiPoint": "MultiPoint",
            "MultiLineString": "LineString",
            "MultiPolygon": "Polygon",
            "GeometryCollection": "SPLIT_BY_GEOMETRY_TYPE",
        }
        Here LineString and MultiLinestring, Polygon and Multipolygon will be in same output geolayer, Point and
        Multipoint geometries in separate Geolayer and entities GeometryCollection will this entity will be duplicated
        according to the geometries it contains.

    :param geolayer: geolayer that we want to split
    :param geometry_type_mapping:
    :yield: split geolayer
    """
    driver_i_feat_geometry_to_filter = _get_driver_geometry_type_matching_i_feat_and_geometry_type_filter(
        geolayer=geolayer,
        geometry_type_mapping=geometry_type_mapping
    )
    # if not split
    if len(driver_i_feat_geometry_to_filter) == 1:
        yield geolayer

    # we create a geolayer by geometry split
    else:
        for (
            driver_geometry_type,
            geolayer_i_feat_and_i_geom,
        ) in driver_i_feat_geometry_to_filter.items():
            # create geolayer
            output_geolayer_metadata = copy.deepcopy(geolayer["metadata"])
            output_geolayer_metadata["geometry_ref"]["type"] = {driver_geometry_type}
            extent_exists = output_geolayer_metadata["geometry_ref"].get("extent")
            if extent_exists:
                del output_geolayer_metadata["geometry_ref"]['extent']
                geolayer_extent = ()
            output_geolayer_metadata["name"] = (
                output_geolayer_metadata["name"] + "_" + driver_geometry_type
            )
            output_geolayer = {"metadata": output_geolayer_metadata, "features": {}}
            output_geolayer_serialize = output_geolayer['metadata'].get("feature_serialize")

            for i, i_feat_and_i_geom in enumerate(geolayer_i_feat_and_i_geom):
                # initialize feature
                feature = {}
                i_feat = i_feat_and_i_geom["i_feat"]
                feature_geometry = i_feat_and_i_geom["feature_geometry"]
                if feature_geometry:
                    if extent_exists:
                        feature_geometry_bbox = feature_geometry.get('bbox')
                        if feature_geometry_bbox:
                            geolayer_extent = bbox_union(bbox_a=geolayer_extent, bbox_b=feature_geometry_bbox)

                    feature["geometry"] = feature_geometry

                # get attributes
                feature_attributes = geolayer["features"][i_feat].get("attributes")
                if feature_attributes:
                    feature["attributes"] = feature_attributes

                if output_geolayer_serialize is True:
                    feature = feature_serialize(feature)
                # put feature in geolayer
                output_geolayer["features"][i] = feature

            # update extent
            if extent_exists:
                if geolayer_extent:
                    output_geolayer['metadata']['extent'] = geolayer_extent

            yield output_geolayer


def feature_list_to_geolayer(
        feature_list,
        geolayer_name,
        field_name_filter=None,
        force_field_conversion=False,
        geometry_type_filter=None,
        bbox_filter=None,
        bbox_extent=True,
        crs=None,
        serialize=False,
        none_value_pattern=none_value_pattern
):
    """
    Create a geolayer with an input feature list.

    :param feature_list: features list that we want to transform to geolayer.
    :param geolayer_name: name for geolayer.
    :param field_name_filter: field_name that we want to keep in geolayer (can be a list).
    :param force_field_conversion: True if you want to force value in field (can change field type) / False if you want
           to deduce field type without forcing field type.
    :param geometry_type_filter: keep only features with geometry type in this variable (can be a list).
    :param bbox_filter: keep only feature that intersects bbox (can be a list of bbox).
    :param bbox_extent: add "bbox" key in each features and "extent" key in geometry metadata.
    :param crs: coordinates spatial reference for geolayer.
    :param serialize: True if features in geolayer are serialized (can reduce performance) / False if not.
    :return: Return geolayer that contains features in feature_list depending on the options specified at the start
    of this function.
    """
    # initialize input variable
    feature_list = value_to_iterable_value(feature_list, list)
    field_name_filter = value_to_iterable_value(field_name_filter, list)
    geometry_type_filter = value_to_iterable_value(geometry_type_filter, list)
    if isinstance(bbox_filter, (list, tuple)):  # TODO remove when bbox will be an object
        if isinstance(bbox_filter[0], (int, float)):  # TODO remove when bbox will be an object
            bbox_filter = [bbox_filter]
    bbox_filter = value_to_iterable_value(bbox_filter, set)

    # initialize output variable
    # create empty _geolayer
    _geolayer = {
        "metadata": {
            "name": geolayer_name
        },
        "features": {

        }
    }
    # metadata
    # get fields metadata
    features_fields_scan = features_fields_type_scan(
        geolayer_or_feature_list=feature_list,
        field_name_filter=field_name_filter,
        try_to_force_type=force_field_conversion,
        fields_index=True,
        none_value_pattern=none_value_pattern
    )
    geolayer_fields_metadata = fields_scan_to_fields_metadata(
        fields_scan=features_fields_scan
    )
    # get geometry metadata
    features_geometries_scan = features_geometry_ref_scan(
        geolayer_or_feature_list=feature_list,
        geometry_type_filter=geometry_type_filter,
        bbox_filter=bbox_filter,
        extent=bbox_extent
    )
    geolayer_geometry_metadata = geometries_scan_to_geometries_metadata(
        geometry_scan=features_geometries_scan,
        crs=crs,
        extent=bbox_extent
    )

    # add metadata to _geolayer
    if geolayer_fields_metadata:
        _geolayer['metadata']['fields'] = geolayer_fields_metadata
    if geolayer_geometry_metadata:
        _geolayer['metadata']['geometry_ref'] = geolayer_geometry_metadata
    if serialize is True:
        _geolayer['metadata']['feature_serialize'] = True

    # add feature to _geolayer
    i_feat = 0

    for feature in feature_list:
        feature = feature_filter(
            feature=feature,
            field_name_filter=field_name_filter,
            geometry_type_filter=geometry_type_filter,
            bbox_filter=bbox_filter,
            bbox=bbox_extent
        )
        # if feature
        if feature:
            # if feature must be serialized
            if serialize:
                feature = feature_serialize(feature)
            _geolayer['features'][i_feat] = feature
            i_feat += 1

    # drop field if necessary
    if geolayer_fields_metadata:
        for field_name, field_dict in features_fields_scan.items():
            if field_dict['field_delete'] is True:
                _geolayer = drop_field(geolayer=_geolayer, field_name_to_drop=field_name)

    # recast field if necessary
    if geolayer_fields_metadata:
        for field_name, field_dict in features_fields_scan.items():
            if field_dict['field_recast'] is True and field_dict['field_delete'] is False:
                # define type to recast
                recast_to_type = _geolayer['metadata']['fields'][field_name]['type']
                # resize width to recast
                resize_width = None
                if 'width' in _geolayer['metadata']['fields'][field_name]:
                    resize_width = _geolayer['metadata']['fields'][field_name]['width']
                # resize precision to recast
                resize_precision = None
                if 'precision' in _geolayer['metadata']['fields'][field_name]:
                    resize_precision = _geolayer['metadata']['fields'][field_name]['precision']
                # recast field in _geolayer
                _geolayer = recast_field(
                    geolayer_to_recast=_geolayer,
                    field_name_to_recast=field_name,
                    recast_to_geoformat_type=recast_to_type,
                    resize_width=resize_width,
                    resize_precision=resize_precision,
                    none_value_pattern=none_value_pattern
                )

    return _geolayer
