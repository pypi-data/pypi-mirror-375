import copy
from pathlib import Path

try:
    import shapefile
    import_shapefile_success = True
except ImportError:
    import_shapefile_success = False


from geoformat.conf.fields_variable import (
    geoformat_field_type_to_shapefile_field_type,
    shapefile_field_type_to_geoformat_field_type,
    python_type_to_geoformat_field_type,
    shapefile_str_max_width,
    field_metadata_width_required,
    field_metadata_precision_required,
)
from geoformat.conf.format_data import value_to_iterable_value
from geoformat.conf.path import verify_input_path_is_dir, path_to_file_path
from geoformat.conf.error_messages import (
    import_shapefile_error,
    geometry_type_does_not_allowed_in_geolayer,
    geometry_type_not_allowed,
    key_parameter_invalid,
    field_name_length_not_valid,
)
from geoformat.conf.geometry_variable import GEOFORMAT_GEOMETRY_TYPE
from geoformat.conversion.coordinates_conversion import format_coordinates
from geoformat.conversion.feature_conversion import (
    features_fields_type_scan,
    feature_filter,
)
from geoformat.manipulation.geolayer_manipulation import feature_list_to_geolayer
from geoformat.conversion.fields_conversion import recast_field_value
from geoformat.conversion.geometry_conversion import geometry_to_bbox, force_rhr
from geoformat.conversion.metadata_conversion import (
    from_field_scan_determine_field_width,
    get_field_name_list_ordered_by_i_field,
)
from geoformat.manipulation.geolayer_manipulation import (
    rename_field,
    split_geolayer_by_geometry_type,
)
from geoformat.manipulation.metadata_manipulation import (
    drop_field_that_not_exists_in_metadata,
)

from geoformat.geoprocessing.geoparameters.bbox import bbox_union
from geoformat.conf.fields_variable import none_value_pattern

shapefile_driver_function_dict = {
    "driver_formating": {
        "max_field_name_char": 10,
        "geometry_mapping": {
            "Point": "Point",
            "LineString": "LineString",
            "Polygon": "Polygon",
            "MultiPoint": "MultiPoint",
            "MultiLineString": "LineString",
            "MultiPolygon": "Polygon",
            "GeometryCollection": "SPLIT_BY_GEOMETRY_TYPE",
        },
        "geometry_type": {
            None: 0,
            "Point": 1,
            "LineString": 3,
            "MultiLineString": 3,
            "Polygon": 5,
            "MultiPolygon": 5,
            "MultiPoint": 8,
        },
        "field_recast": True,
        "format_field_type": {
            "IntegerList": str,
            "RealList": str,
            "StringList": str,
            "Time": str,
            "DateTime": str,
            "Binary": str,
        },
        "field_type_necessary_metadata": {
            "C": {"width"},
            "N": {"width", "precision"},
            "F": {"width", "precision"},
            "L": None,
            "D": None,
        },
        "format_feature_data": {
            "D": {
                "module": "geoformat",
                "function_name": "format_datetime_object_to_str_value",
                "need_parameters_name": "datetime_value",
                "default_parameters": {"format": ["year", "month", "day"]},
            }
        },
    },
    "layer_creator": {
        "create_layer": {
            "module": "shapefile",
            "function_name": "Writer",
            "need_parameters": {"target": "PATH", "shapeType": "OUTPUT_GEOMETRY_TYPE"},
            "default_parameters": {"autoBalance": False},
        },
        "create_field": {
            "function_name": "field",
            "module": "create_layer",
            "method_child_from": "create_layer",
            "need_parameters_name": {
                "name": "new_field_name",
                "fieldType": "type",
                "size": "width",
                "decimal": "precision",
            },
            "default_field": {"id": {"type": "Integer"}},
        },
        "create_feature_attributes": {
            "function_name": "record",
            "module": "create_layer",
            "need_parameters_name": "recordList",  # we can use recordDict too
            "method_child_from": "create_layer",
        },
        "create_feature_geometry": {
            "function_name": "shape",
            "need_parameters_name": "recordList",  # we can use recordDict too
            "method_child_from": "create_layer",
        },
    },
}

pyshp_geometry_type = {
    0: None,
    1: "Point",
    3: "LineString",
    5: "Polygon",
    8: "MultiPoint",
}


def _get_module(metadata_dict, locals_var=None):
    """
    Return module wanted in metadata dict.

    :param metadata_dict:  dict with information to catch function
    :param locals_var: local variable
    :return: return wanted module
    """

    if locals_var is None:
        locals_var = {}

    module_name = metadata_dict.get("module")

    if module_name in locals_var:
        module = locals_var[module_name]
    # if module is string we have to import it
    else:
        module = __import__(
            name=module_name,
            locals=None,
            globals=None,
            fromlist=metadata_dict.get("function_name", ()),
            level=0,
        )

    return module


def _get_function(metadata_dict, locals_var=None):
    """
    Return function wanted in metadata_dict.

    :param metadata_dict: dict with information to catch function
    :param locals_var: script local variables and functions (get with locals() function).
    :return: return wanted function
    """
    module = _get_module(metadata_dict, locals_var=locals_var)
    function_name = metadata_dict["function_name"]
    # get function
    function = getattr(module, function_name)

    return function


def _format_coordinates_for_pyshp(geometry):
    """
    return geometry coordinates dict formatted to PyShp lib formatting coordinates.

    :param: Geoformat geometry.
    :return: dict with input variable with associated data in it for writing geometry in pyshp.
    """
    geometry_type = geometry.get("type")
    if geometry_type.upper() in GEOFORMAT_GEOMETRY_TYPE:
        geometry_coordinates = geometry.get("coordinates")
        return_coordinates = {}
        if geometry_type == "Point":
            return_coordinates = {
                "x": geometry_coordinates[0],
                "y": geometry_coordinates[1],
            }
        elif geometry_type == "LineString":
            return_coordinates = {"lines": [geometry_coordinates]}
        elif geometry_type == "Polygon":
            return_coordinates = {"polys": geometry_coordinates}
        elif geometry_type == "MultiPoint":
            return_coordinates = {"points": geometry_coordinates}
        elif geometry_type == "MultiLineString":
            return_coordinates = {"lines": geometry_coordinates}
        elif geometry_type == "MultiPolygon":
            flat_coordinates = []
            for poly in geometry_coordinates:
                flat_coordinates = flat_coordinates + poly
            return_coordinates = {"polys": flat_coordinates}
    else:
        raise Exception(geometry_type_not_allowed.format(geometry_type=geometry_type))

    return return_coordinates


def _esri_shapefile_check_fields_metadata(_geolayer, _driver_parameters):
    """
    Scan geolayer metadata and use driver parameters to check if fields must be recast or not.
    If field(s) must be recast this function return a dict formatted like this :
        {
            field_name: {     # field name that must be recast
                "recast_value_to_python_type": # python type of recasting,
                "recast_value_to_output_type": # output format type (depend on driver)
                "resize_value_width": # new value's width,
                "resize_value_precision": # new value's precision}
        }

    :param _geolayer: input geolayer
    :param _driver_parameters: esri shapefile driver parameters
    :return: dict (describes below) that contains field name to recast and parameters for recasting
    """
    field_recast = _driver_parameters["driver_formating"].get("field_recast", False)

    # scan field metadata to check if field must have to be recast
    fields_metadata = _geolayer["metadata"].get("fields", {})
    recast_field_mapping = {}
    recast_field_scan_list = []
    for field_name, field_metadata in fields_metadata.items():
        # check if field geoformat must be recast in output format
        recast_to_python_type = _driver_parameters["driver_formating"][
            "format_field_type"
        ].get(field_metadata["type"], None)
        if recast_to_python_type:
            recast_field_mapping[field_name] = {
                "recast_value_to_python_type": recast_to_python_type,
                "recast_value_to_output_type": geoformat_field_type_to_shapefile_field_type[
                    python_type_to_geoformat_field_type[recast_to_python_type]
                ],
                "resize_value_width": None,
                "resize_value_precision": None,
            }
        # if recasting is necessary
        if recast_to_python_type is not None:
            if field_recast is True:
                recast_field_scan_list.append(field_name)

    # scan all fields that will be recast to have information about (width and precision)
    if field_recast and recast_field_scan_list:
        # scan values that must be recast
        field_scan = features_fields_type_scan(
            geolayer_or_feature_list=_geolayer,
            field_name_filter=recast_field_scan_list,
            try_to_force_type=False,
        )

        # put result in output dict
        for field_name in recast_field_scan_list:
            field_name_scan_dict = field_scan[field_name]
            recast_field_name_dict = recast_field_mapping[field_name]
            recast_to_python_type = recast_field_name_dict[
                "recast_value_to_python_type"
            ]
            recast_to_shapefile_type = recast_field_name_dict[
                "recast_value_to_output_type"
            ]
            # get needed metadata
            output_field_type_metadata_need = _driver_parameters["driver_formating"][
                "field_type_necessary_metadata"
            ][recast_to_shapefile_type]
            if "width" in output_field_type_metadata_need:
                field_in_list = False
                if isinstance(recast_to_python_type, tuple):
                    field_in_list = True

                field_name_width = from_field_scan_determine_field_width(
                    field_type=recast_to_python_type,
                    field_in_list=field_in_list,
                    field_width_str=field_name_scan_dict["field_width_str"],
                    field_width_float=field_name_scan_dict["field_width_float"],
                    field_width_list=field_name_scan_dict["field_width_list"],
                    max_width=shapefile_str_max_width,
                )
                recast_field_name_dict["resize_value_width"] = field_name_width

            if "precision" in output_field_type_metadata_need:
                recast_field_name_dict["resize_value_precision"] = field_name_scan_dict[
                    "field_precision"
                ]

    return recast_field_mapping


def _geoformat_feature_to_shapefile_feature(
    feature,
    shapefile_fields_metadata,
    recast_field_mapping,
    shapefile_format_value,
    locals_var=None,
):
    """
    Convert geoformat feature to shapefile feature.

    :param feature: geoformat feature
    :param shapefile_fields_metadata: shapefile field object
    :param recast_field_mapping: dict with field to recast and parameters to recast it
    :param shapefile_format_value: dict that describe how to reformat certain type of shapefile value to be compatible
     with geoformat values
    :param locals_var: locals variable or function.
    """
    output_feature = copy.deepcopy(feature)
    # attributes
    feature_attributes = output_feature.get("attributes", {})
    if feature_attributes:
        # recast field if necessary
        for field_name, field_name_recast in recast_field_mapping.items():
            feature_attributes[field_name] = recast_field_value(
                field_value=feature_attributes[field_name],
                recast_value_to_python_type=field_name_recast[
                    "recast_value_to_python_type"
                ],
                # recast_value_in_list=field_name_recast['recast_value_in_list'],
                resize_value_width=field_name_recast["resize_value_width"],
                resize_value_precision=field_name_recast["resize_value_precision"],
            )
        # reformat data
        if shapefile_format_value:
            for field_name, shp_field_metadata in shapefile_fields_metadata.items():
                reformat_dict_for_field_type = shapefile_format_value.get(
                    shp_field_metadata.get("fieldType")
                )
                if reformat_dict_for_field_type:
                    # get reformat_function
                    reformat_function = _get_function(
                        reformat_dict_for_field_type, locals_var=locals_var
                    )
                    # init parameters
                    parameters = reformat_dict_for_field_type["default_parameters"]
                    # add value to reformat in parameters
                    parameters[
                        reformat_dict_for_field_type["need_parameters_name"]
                    ] = feature_attributes[field_name]
                    # rewrite in feature data with reformat function
                    feature_attributes[field_name] = reformat_function(**parameters)

    return output_feature


def _esri_shapefile_format_field_metadata(
    _geolayer, _driver_parameters, _recast_field_mapping
):
    """
    Return field metadata for output format.

    Indeed, some geoformat field types are not necessarily compatible with the output driver
    (so they have to be recast). Also, the type of fields in the output format do not always
     require the same metadata (we must therefore sort them).

    This function return a dictionary indicating for each field the type in the output format
    and the required metadata with it.

    :param _geolayer: geolayer.
    :param _driver_parameters: driver parameters.
    :param _recast_field_mapping: dict that contains field to recast and parameters for recasting.
    :return: shapefile field metadata
    """
    # make dictionary with output format field type correspondance metadata in it
    shapefile_fields_metadata = {}
    default_field = {
        "id": {"type": "Integer"}
    }  # TODO GET shapefile_driver_function_dict
    geoformat_fields_metadata = _geolayer["metadata"].get("fields", default_field)
    for field_name in geoformat_fields_metadata:
        geoformat_field_type = geoformat_fields_metadata[field_name]["type"]
        shapefile_field_type = geoformat_field_type_to_shapefile_field_type.get(
            geoformat_field_type
        )
        shapefile_field_size = geoformat_fields_metadata[field_name].get("width", None)
        shapefile_field_decimal = geoformat_fields_metadata[field_name].get(
            "precision", None
        )
        if field_name in _recast_field_mapping:
            if _recast_field_mapping[field_name]["recast_value_to_output_type"]:
                shapefile_field_type = _recast_field_mapping[field_name][
                    "recast_value_to_output_type"
                ]
            if _recast_field_mapping[field_name]["resize_value_width"]:
                shapefile_field_size = _recast_field_mapping[field_name][
                    "resize_value_width"
                ]
            if _recast_field_mapping[field_name]["resize_value_precision"]:
                shapefile_field_decimal = _recast_field_mapping[field_name][
                    "resize_value_precision"
                ]
        # add + 1 size for number and float type
        if shapefile_field_type in {"N", "F"}:
            if (
                shapefile_field_decimal is not None and shapefile_field_decimal > 0
            ):  # if there is number after comma
                shapefile_field_size += 1
        # TODO big refacto here
        # TODO is it overkill ? Response : YES
        shapefile_matching_field_variable_dict = {
            0: "name",
            1: "fieldType",
            2: "size",
            3: "decimal",
        }
        field_metadata_list = [
            field_name,
            shapefile_field_type,
            shapefile_field_size,
            shapefile_field_decimal,
        ]
        shapefile_field_variable = {}
        for i_metadata, field_metadata in enumerate(field_metadata_list):
            if field_metadata:
                shapefile_field_variable[
                    shapefile_matching_field_variable_dict[i_metadata]
                ] = field_metadata
        # save shapefile field metadata
        shapefile_fields_metadata[field_name] = shapefile_field_variable

    return shapefile_fields_metadata


def _write_layer(
    _geolayer,
    _output_path,
    _driver_parameters,
    _esri_shapefile_field_metadata,
    _output_field_recast_mapping,
    encoding,
):
    """
    From geolayer to esri shapefile files.

    :param _geolayer: geolayer that will be converted to a shapefile.
    :param _output_path: path for output file
    :param _driver_parameters: esri shapefile driver parameters
    :param _esri_shapefile_field_metadata: esri shapefile field metadata
    :param _output_field_recast_mapping:  dict that contains field name to recast and parameters for recasting
    :param encoding: output encoding string wanted
    """
    # CREATE LAYER
    # create_layer_metadata_dict = driver_function_dict['create_layer']  # TODO DELELE
    create_layer_metadata_dict = _driver_parameters["layer_creator"]["create_layer"]
    create_layer_function = _get_function(create_layer_metadata_dict)

    # fill need parameters
    create_layer_parameters = {}
    layer_creator_need_parameter = create_layer_metadata_dict.get("need_parameters")
    if layer_creator_need_parameter:
        for need_parameter_name, key in create_layer_metadata_dict[
            "need_parameters"
        ].items():
            if key == "PATH":
                key_value = _output_path
                # if no geometry in geolayer we only create a dbf
                if _geolayer["metadata"].get("geometry_ref") is None:
                    need_parameter_name = "dbf"

            elif key == "OUTPUT_GEOMETRY_TYPE":
                geolayer_geometry_ref = _geolayer["metadata"].get("geometry_ref")
                if geolayer_geometry_ref:
                    geolayer_geometry_type = geolayer_geometry_ref["type"]
                    geometry_type_set = set()
                    for geometry_type in geolayer_geometry_type:
                        output_geometry_type = _driver_parameters["driver_formating"][
                            "geometry_type"
                        ][geometry_type]
                        geometry_type_set.update([output_geometry_type])
                    if len(geometry_type_set) == 1:
                        key_value = list(geometry_type_set)[0]
                    else:
                        raise Exception(
                            geometry_type_does_not_allowed_in_geolayer.format(
                                geometry_type=geometry_type_set
                            )
                        )
                else:
                    continue  # if no geometry_ref in geolayer we create only the dbf
                    # then we do not need geometry_type parameter
            else:
                raise Exception(key_parameter_invalid.format(key=key))

            create_layer_parameters[need_parameter_name] = key_value
    create_layer_parameters = {
        **create_layer_metadata_dict["default_parameters"],
        **create_layer_parameters,
    }

    with create_layer_function(
        **create_layer_parameters, encoding=encoding
    ) as create_layer:

        # get method and parameters for field creation
        # get parameters
        field_creator_dict = _driver_parameters["layer_creator"]["create_field"]
        # get method
        field_creator_method = _get_function(field_creator_dict, locals_var=locals())

        # get parameters and associate method for feature creation
        # get parameters
        create_feature_attributes_dict = _driver_parameters["layer_creator"][
            "create_feature_attributes"
        ]
        # get method
        create_feature_attributes_method = _get_function(
            create_feature_attributes_dict, locals_var=locals()
        )
        # CREATE FIELD
        # test if there is mother class to create field
        mother_class_for_create_field = _driver_parameters["layer_creator"][
            "create_field"
        ].get("method_child_from")
        if mother_class_for_create_field:
            # reformat field name (if necessary)
            ori_field_name_list = get_field_name_list_ordered_by_i_field(
                fields_metadata=_esri_shapefile_field_metadata
            )
            max_field_name_char = _driver_parameters["driver_formating"].get(
                "max_field_name_char"
            )
            new_field_name_list = _esri_shapefile_rename_field_list(
                field_name_list=ori_field_name_list,
                max_field_name_char=max_field_name_char,
            )

            for i_field, new_field_name in enumerate(new_field_name_list):
                ori_field_name = ori_field_name_list[i_field]
                shp_field_metadata = _esri_shapefile_field_metadata[ori_field_name]
                shp_field_metadata["name"] = new_field_name

                field_creator_method(**shp_field_metadata)

        # CREATE FEATURE
        # get geolayer fields metadata
        fields_metadata = _geolayer["metadata"].get("fields", None)
        for i_feat, feature in _geolayer["features"].items():

            shapefile_feature = _geoformat_feature_to_shapefile_feature(
                feature=feature,
                shapefile_fields_metadata=_esri_shapefile_field_metadata,
                recast_field_mapping=_output_field_recast_mapping,
                shapefile_format_value=_driver_parameters["driver_formating"][
                    "format_feature_data"
                ],
                locals_var=locals(),
            )
            if shapefile_feature.get("attributes"):
                feature_shapefile_values = [
                    shapefile_feature["attributes"].get(field_name, None)
                    for field_name in fields_metadata
                ]

                # create_feature_attributes_method = getattr(layer, create_feature_attributes_method_name)
                create_feature_attributes_method(*feature_shapefile_values)
            else:
                create_layer.record(i_feat)

            if create_layer.shapeType is not None:  # if not only dbf file
                if feature_geometry := shapefile_feature.get("geometry"):
                    feature_geometry_type = feature_geometry.get("type")
                    feature_geometry_coordinates = feature_geometry.get("coordinates")
                    if not feature_geometry_coordinates:
                        create_layer.null()
                    else:
                        if feature_geometry_type == "Point":
                            create_feature_geometry = create_layer.point
                        elif feature_geometry_type in {"LineString", "MultiLineString"}:
                            create_feature_geometry = create_layer.line
                        elif feature_geometry_type in {"Polygon", "MultiPolygon"}:
                            create_feature_geometry = create_layer.poly
                            # use force rhr
                            feature_geometry = force_rhr(
                                polygon_geometry=feature_geometry
                            )
                        elif feature_geometry_type == "MultiPoint":
                            create_feature_geometry = create_layer.multipoint
                        # write geometry in feature
                        create_feature_geometry(
                            **_format_coordinates_for_pyshp(geometry=feature_geometry)
                        )
                else:
                    create_layer.null()


def geolayer_to_shapefile(
    geolayer,
    path,
    overwrite=False,
    encoding="utf8",
):
    """
    Convert geolayer to esri shapefile file.

    :param geolayer: input geolayer to convert.
    :param path: output file or directory path.
    :param overwrite: True we overwrite if exists false we raise an exception.
    :param encoding: string encoding default utf8
    """
    if import_shapefile_success is False:
        raise Exception(import_shapefile_error)

    # get shapefile driver dict
    driver_parameters = shapefile_driver_function_dict

    # check fields metadata and identifies the fields that must be recast
    output_field_recast_mapping = _esri_shapefile_check_fields_metadata(
        _geolayer=geolayer, _driver_parameters=driver_parameters
    )

    # get adjusted field metadata
    esri_shapefile_field_metadata = _esri_shapefile_format_field_metadata(
        _geolayer=geolayer,
        _driver_parameters=driver_parameters,
        _recast_field_mapping=output_field_recast_mapping,
    )

    # check geometry compatibility
    geometry_metadata = geolayer["metadata"].get("geometry_ref")
    geometry_mapping = driver_parameters["driver_formating"].get("geometry_mapping")
    if geometry_metadata and geometry_mapping:
        geolayer_list = list(
            split_geolayer_by_geometry_type(
                geolayer=geolayer, geometry_type_mapping=geometry_mapping
            )
        )
    else:
        geolayer_list = [geolayer]

    # we have multi geolayer to create then path must be a folder not a file
    if len(geolayer_list) > 1:
        verify_input_path_is_dir(path=path)

    for i_geolayer, _geolayer in enumerate(geolayer_list):
        if _geolayer["metadata"].get("geometry_ref"):
            add_extension = ".shp"
        else:
            add_extension = ".dbf"

        # verify output path
        output_path = path_to_file_path(
            path=path,
            geolayer_name=_geolayer["metadata"]["name"],
            overwrite=overwrite,
            add_extension=add_extension,
        )

        # write layer
        _write_layer(
            _geolayer=_geolayer,
            _output_path=output_path,
            _driver_parameters=driver_parameters,
            _esri_shapefile_field_metadata=esri_shapefile_field_metadata,
            _output_field_recast_mapping=output_field_recast_mapping,
            encoding=encoding,
        )


def _shapefile_fields_to_geoformat_field_metadata(
    shp_fields, shp_rename_field_name_list
):
    """
    Deduce geoformat field metadata for shapefile field parameters

    :param shp_fields: shapefile field object
    :param shp_rename_field_name_list: list that contains output field name
    :return: geoformat geolayer field metadata
    """
    geoformat_field_metadata = {}
    field_index = 0

    # loop on each field and create geolayer metadata
    for i_field, shp_metadata_field in enumerate(shp_fields):
        (
            shp_ori_field_name,
            shp_field_type,
            shp_width,
            shp_precision,
        ) = shp_metadata_field
        shp_field_name = shp_rename_field_name_list[i_field]
        if shp_ori_field_name != "DeletionFlag":
            geoformat_field_type = shapefile_field_type_to_geoformat_field_type.get(
                shp_field_type
            )
            if geoformat_field_type == "Real":
                if shp_precision == 0:
                    geoformat_field_type = "Integer"
                else:
                    shp_width -= 1  # esri shapefile count real comma in width
            geoformat_field_metadata[shp_field_name] = {"type": geoformat_field_type}
            if geoformat_field_type in field_metadata_width_required:
                geoformat_field_metadata[shp_field_name]["width"] = shp_width
            if geoformat_field_type in field_metadata_precision_required:
                geoformat_field_metadata[shp_field_name]["precision"] = shp_precision

            geoformat_field_metadata[shp_field_name]["index"] = field_index
            field_index += 1

    return geoformat_field_metadata


def _get_record_to_layer(layer, feature_offset=None, feature_limit=None):
    """
    Yield record (feature) of layer. You can add offset and limit parameters to have only some record and not all
     layer's records.

    :param layer: shapefile layer object
    :param feature_offset: says to skip that many records before beginning to return record
    :param feature_limit: says the maximum number of records to yield
    :yield: record
    """
    # if just dbf in input
    if layer.shp is None:
        layer = layer.records()

    yield_count = 0
    for i_feat, record in enumerate(layer):
        if feature_offset:
            if i_feat < feature_offset:
                continue

        if record:
            # if just dbf we create a ShapeRecord object for record
            if not isinstance(record, shapefile.ShapeRecord):
                record = shapefile.ShapeRecord(record=record)
            yield record
            yield_count += 1

            if feature_limit:
                if yield_count == feature_limit:
                    break


def _shapefile_record_to_geoformat_feature(
    record,
    selected_field_shapefile_index,
    ordered_field_name_list,
    layer_shape_type,
    pyshp_geometry_type,
    bbox_extent,
):
    """
    Convert shapefile record (feature) to geoformat feature

    :param record: shapefile record
    :param selected_field_shapefile_index: list of field index in
    :param ordered_field_name_list: field name list
    :param layer_shape_type: shapefile geometry type
    :param pyshp_geometry_type: correspondance table between pyshp geometry number and str geometry type
    :param bbox_extent: True we add bbox to feature/ False we don't
    """
    feature = {}
    # attributes
    if record.record and selected_field_shapefile_index is not None:
        feature["attributes"] = {}
        for i_field, shp_i_field in enumerate(selected_field_shapefile_index):
            field_value = record.record[shp_i_field]
            feature["attributes"][ordered_field_name_list[i_field]] = field_value

    # geometry
    if layer_shape_type:
        if record.shape:
            if record.shape.shapeType:
                feature_geometry = record.shape.__geo_interface__
                feature_geometry["coordinates"] = format_coordinates(
                    coordinates_list_tuple=feature_geometry["coordinates"],
                    format_to_type=list,
                )
            else:
                feature_geometry = {
                    "type": pyshp_geometry_type[layer_shape_type],
                    "coordinates": [],
                }

            # add bbox (if required)
            if bbox_extent is True and feature_geometry["coordinates"]:
                if record.shape.shapeType != 1:
                    bbox = tuple(record.shape.bbox)
                else:
                    bbox = geometry_to_bbox(geometry=feature_geometry)
                feature_geometry["bbox"] = bbox

            if feature_geometry:
                # add geometry to feature
                feature["geometry"] = feature_geometry

    return feature


def shapefile_to_geolayer(
    path,
    field_name_filter=None,
    rename_field_dict=None,
    bbox_extent=True,
    bbox_filter=None,
    serialize=False,
    geometry_type_filter=None,
    feature_limit=None,
    feature_offset=None,
    force_field_conversion=False,
    crs=None,
    encoding="utf8",
):
    """
    Convert esri shapefile file to geolayer

    :param path: path to geojson file
    :param field_name_filter: field_name that we want to keep in geolayer (can be a list).
    :param rename_field_dict: dict as table of correspondance to rename field.
    :param bbox_extent: add "bbox" key in each feature and "extent" key in geometry metadata.
    :param bbox_filter: keep only feature that intersects bbox (can be a list of bbox).
    :param serialize: True if features in geolayer are serialized (can reduce performance) / False if not.
    :param geometry_type_filter: keep only features with geometry type in this variable (can be a list).
    :param feature_limit: constrains the number of rows returned in output geolayer.
    :param feature_offset: skip feature before beginning to given line number.
    :param force_field_conversion:  True if you want to force value in field (can change field type) / False if you want
           to deduce field type without forcing field type.
    :param crs: epsg code for coordinates reference system.
    :param encoding: string encoding default utf8
    """

    if import_shapefile_success is False:
        raise Exception(import_shapefile_error)

    field_name_filter = value_to_iterable_value(
        field_name_filter, output_iterable_type=list
    )

    with shapefile.Reader(path, encoding=encoding) as shp:
        geolayer_name = Path(shp.shapeName).name
        output_geolayer = {"metadata": {"name": geolayer_name}, "features": {}}
        # get fields metadata
        # rename field name if necessary
        shp_field_obj = shp.fields
        shp_field_name_list = [
            shp_metadata_field[0] for shp_metadata_field in shp_field_obj
        ]
        shp_rename_field_name_list = _esri_shapefile_rename_field_list(
            field_name_list=shp_field_name_list, max_field_name_char=None
        )
        geolayer_metadata_fields = _shapefile_fields_to_geoformat_field_metadata(
            shp_fields=shp_field_obj,
            shp_rename_field_name_list=shp_rename_field_name_list,
        )
        shapefile_ordered_field_name_list = get_field_name_list_ordered_by_i_field(
            fields_metadata=geolayer_metadata_fields
        )
        if geolayer_metadata_fields:
            output_geolayer["metadata"]["fields"] = geolayer_metadata_fields

        if field_name_filter is not None:
            output_geolayer["metadata"] = drop_field_that_not_exists_in_metadata(
                metadata=output_geolayer["metadata"],
                not_deleting_field_name_or_field_name_list=field_name_filter,
            )

        geolayer_metadata_fields = output_geolayer["metadata"].get("fields")

        # re order fields
        ordered_field_name_list = None
        selected_field_shapefile_index = None
        if geolayer_metadata_fields:
            # create correspondence table between field order in shapefile and kipped field in geolayer
            ordered_field_name_list = get_field_name_list_ordered_by_i_field(
                fields_metadata=output_geolayer["metadata"]["fields"]
            )
            selected_field_shapefile_index = [
                shapefile_ordered_field_name_list.index(field_name)
                for field_name in geolayer_metadata_fields
            ]

        # get geometry metadata
        layer_shape_type = None
        if shp.shp is not None:
            layer_shape_type = shp.shapeType
            if layer_shape_type != 0:
                output_geolayer["metadata"]["geometry_ref"] = {"type": set()}
                if bbox_extent is True:
                    output_geolayer["metadata"]["geometry_ref"]["extent"] = tuple(
                        shp.bbox
                    )

        i_feat = 0
        for record in _get_record_to_layer(
            layer=shp, feature_limit=feature_limit, feature_offset=feature_offset
        ):
            feature = _shapefile_record_to_geoformat_feature(
                record=record,
                selected_field_shapefile_index=selected_field_shapefile_index,
                ordered_field_name_list=ordered_field_name_list,
                layer_shape_type=layer_shape_type,
                pyshp_geometry_type=pyshp_geometry_type,
                bbox_extent=bbox_extent,
            )
            feature = feature_filter(
                feature=feature,
                serialize=serialize,
                field_name_filter=field_name_filter,
                geometry_type_filter=geometry_type_filter,
                bbox_filter=bbox_filter,
                bbox=bbox_extent,
            )
            if feature:
                output_geolayer["features"][i_feat] = feature
                # add metadata geolayer
                feature_geometry = feature.get("geometry")
                if feature_geometry:
                    output_geolayer["metadata"]["geometry_ref"]["type"].update(
                        [feature_geometry["type"]]
                    )
                    if bbox_filter or geometry_type_filter:
                        feature_geometry_bbox = geometry_to_bbox(feature_geometry)
                        if i_feat == 0:
                            geolayer["geometry_ref"]["extent"] = feature_geometry_bbox
                        else:
                            geolayer["geometry_ref"]["extent"] = bbox_union(
                                feature_geometry_bbox,
                                geolayer["geometry_ref"]["extent"],
                            )
                i_feat += 1

        if force_field_conversion is True:
            output_geolayer = feature_list_to_geolayer(
                feature_list=[
                    feature for i_feat, feature in output_geolayer["features"].items()
                ],
                geolayer_name=output_geolayer["metadata"]["name"],
                field_name_filter=None,
                force_field_conversion=force_field_conversion,
                geometry_type_filter=None,
                bbox_filter=None,
                bbox_extent=bbox_extent,
                crs=crs,
                serialize=serialize,
                none_value_pattern=none_value_pattern,
            )

        if rename_field_dict:
            for field_name, new_field_name in rename_field_dict.items():
                output_geolayer = rename_field(
                    geolayer=output_geolayer,
                    old_field_name=field_name,
                    new_field_name=new_field_name,
                )

    return output_geolayer


def _esri_shapefile_rename_field_list(field_name_list, max_field_name_char=None):
    """
    This function rename field_name contains in a list.
    The return field has a length less than or equal to the variable max_field_name_char

    :param field_name_list: list of field to rename
    :param max_field_name_char: maximum number of characters
    :return: list with renamed field_name
    """
    new_field_name_set = set()
    result_field_list = [None] * len(field_name_list)
    for i_field, field_name in enumerate(field_name_list):
        if max_field_name_char:
            new_field_name = field_name[:max_field_name_char]
            new_max_field_length = max_field_name_char
        else:
            new_field_name = field_name
            new_max_field_length = len(field_name)

        if new_field_name in new_field_name_set:
            exists = True
            it = 1
            new_field_name = field_name
            while exists is True:
                len_it = len(str(it))
                max_field_lenght_with_length_it = new_max_field_length - len_it
                if (
                    max_field_lenght_with_length_it < 1
                ):  # alway keep the first letter of input field_name
                    raise Exception(
                        field_name_length_not_valid.format(
                            variable_name=max_field_name_char
                        )
                    )
                new_field_name = new_field_name[:max_field_lenght_with_length_it]

                new_field_name = f"{new_field_name}{it}"
                if new_field_name in new_field_name_set:
                    it += 1
                else:
                    exists = False

        result_field_list[i_field] = new_field_name
        new_field_name_set.update([new_field_name])

    return result_field_list
