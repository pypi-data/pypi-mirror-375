import csv
import json

from geoformat.conf.error_messages import geometry_format_not_exists
from geoformat.conf.fields_variable import geoformat_field_type_to_csv_field_type
from geoformat.conf.fields_variable import none_value_pattern
from geoformat.conf.geoformat_var import GEOLAYER_DEFAULT_NAME
from geoformat.conf.path import path_to_file_path
from geoformat.conversion.feature_conversion import feature_filter
from geoformat.manipulation.geolayer_manipulation import feature_list_to_geolayer
from geoformat.conversion.fields_conversion import recast_field_value
from geoformat.conversion.geometry_conversion import (
    geometry_to_wkb,
    geometry_to_wkt,
    wkb_to_geometry,
    wkt_to_geometry,
)
from geoformat.conversion.metadata_conversion import (
    get_field_name_list_ordered_by_i_field,
)
from geoformat.driver.common_driver import _get_recast_field_type_mapping
from geoformat.driver.common_driver import load_data


def _from_csv_get_features_list(
    csv_reader,
    header,
    serialize,
    field_name_filter,
    geometry_field,
    geometry_field_name,
    geometry_format,
    geometry_type_filter,
    bbox_filter,
    bbox
):
    """
    Take csv reader object and yield csv row into geoformat feature

    :param csv_reader: csv reader object.
    :param header: Specifies that the file contains a header line with the names of each column in the file. (bool)

    :return: geoformat Feature
    """
    for i_row, row in enumerate(csv_reader):
        if i_row == 0:
            if header is True:
                field_name_list = list(row)
                continue
            else:
                field_name_list = [
                    "field_{}".format(i_field) for i_field in range(len(row))
                ]

        feature = {}
        feature["attributes"] = {
            field_name: row[i_field]
            for i_field, field_name in enumerate(field_name_list)
        }

        if geometry_field is True:
            geometry_as_attributes = feature["attributes"].get(
                geometry_field_name
            )
            if geometry_format in {"WKT", "WKB", "GEOJSON"}:
                if geometry_format == "WKT":
                    geoformat_geometry = wkt_to_geometry(geometry_as_attributes, bbox=bbox)
                elif geometry_format == "WKB":
                    geoformat_geometry = wkb_to_geometry(geometry_as_attributes, bbox=bbox)
                else:  # GEOJSON
                    geoformat_geometry = json.loads(geometry_as_attributes)
            else:
                raise Exception(geometry_format_not_exists)

            if geoformat_geometry:
                feature["geometry"] = geoformat_geometry
                # delete feature attributes for geometry_field_name
                del feature["attributes"][geometry_field_name]

        feature = feature_filter(
            feature=feature,
            serialize=serialize,
            field_name_filter=field_name_filter,
            geometry_type_filter=geometry_type_filter,
            bbox_filter=bbox_filter,
            bbox=bbox
        )
        if feature:
            yield feature


def csv_to_geolayer(
    path,
    geolayer_name=None,
    delimiter=";",
    header=True,
    null_string='',
    # quote_character='', TODO
    field_name_filter=None,
    force_field_conversion=False,
    serialize=False,
    encoding="utf8",
    geometry_field=False,
    geometry_field_name=None,
    geometry_type_filter=None,
    geometry_format="WKT",
    crs="",
    bbox_extent= False,
    bbox_filter= None,
    http_headers=None
):
    """
    From csv file get a geolayer.

    :param path: path to csv file
    :param delimiter: Specifies the character that separates columns within each row (line) of the file.
     The default is comma character.
    :param header: Specifies that the file contains a header line with the names of each column in the file. (bool)
    :param field_name_filter: filter only on specified field_name (can be a list)
    :param force_field_conversion: True if you want to force value in field (can change field type) / False if you want
           to deduce field type without forcing field type.
    :param serialize: True if features in geolayer are serialized (can reduce performance) / False if not.
    :param geometry_field:
    :param geometry_field_name: field's name that contain geometry
    :param geometry_format: geometry format (WKT / WKB or GEOJSON)
    :param encoding: string encoding default utf8
    :param http_headers: optionally you can add headers of http parameters

    :return: geolayer
    """

    # update none_value_pattern variable
    if null_string is not None:
        none_value_pattern.update([null_string])

    # with open(p, "r", encoding=encoding) as csv_file:
    csv_file, csv_name = load_data(path=path, encoding=encoding, http_headers=http_headers)
    geolayer_name = geolayer_name or csv_name or GEOLAYER_DEFAULT_NAME
    with open(csv_file.name, 'r') as csv_data:
        raw_feature_list = csv.reader(csv_data, delimiter=delimiter)
        raw_feature_list = list(
            _from_csv_get_features_list(
                csv_reader=raw_feature_list,
                header=header,
                serialize=serialize,
                field_name_filter=field_name_filter,
                geometry_field=geometry_field,
                geometry_field_name=geometry_field_name,
                geometry_format=geometry_format,
                geometry_type_filter=geometry_type_filter,
                bbox_filter=bbox_filter,
                bbox=bbox_extent
            )
        )
        geolayer = feature_list_to_geolayer(
            feature_list=raw_feature_list,
            geolayer_name=geolayer_name,
            force_field_conversion=force_field_conversion,
            bbox_extent=bbox_extent,
            crs=crs,
            serialize=serialize,
            none_value_pattern=none_value_pattern,
        )

    return geolayer


def geoformat_feature_to_csv_feature(
    feature,
    recast_field_mapping,
    string_field_name,
    null_string,
    quote_character,
    write_geometry,
    geometry_format,
):
    """
    Make transformation between geoformat feature to geojson feature.

    :param feature: geoformat feature
    :param recast_field_mapping: dict that contains field to recast and parameters to recast
    :param string_field_name: field's name
    :param null_string: how to format in csv format None value
    :param quote_character: quote character in csv to describe string value
    :param write_geometry: True if you want write geometry field in csv
    :param geometry_format: convert geometry to output format

    :return: dict like geoformat feature but with attributes and geometry in csv format
    """
    geometry = {}
    if write_geometry is True:
        # get geometries
        geometry = dict(feature.get("geometry", {}))
        if geometry:
            # delete bbox if exists
            geometry.pop("bbox", None)
            if geometry_format == "WKT":
                geometry = geometry_to_wkt(geometry)
            elif geometry_format == "WKB":
                geometry = geometry_to_wkb(geometry).hex()
            elif geometry_format == "GEOJSON":
                geometry = json.dumps(geometry)
            else:
                raise Exception(geometry_format_not_exists)

    # get attributes and clean it
    attributes = dict(feature.get("attributes", {}))
    attributes = feature_attributes_to_csv_attributes(attributes, recast_field_mapping)

    for field_name, value in attributes.items():
        if field_name in string_field_name:
            attributes[field_name] = "{}{}{}".format(
                quote_character, value, quote_character
            )
        if value is None:
            attributes[field_name] = null_string

    return {"attributes": attributes, "geometry": geometry}


def feature_attributes_to_csv_attributes(attributes, recast_field_mapping=None):
    """
    Transforms feature's attributes to geojson properties

    :param attributes: feature attributes
    :param recast_field_mapping: config dict to recast field to geojson properties format
    :return: formatted geojson properties
    """
    if attributes:
        # check is data are serialized or not
        csv_attributes = dict(attributes)
        # if recast_field_mapping
        if recast_field_mapping is not None:
            for field_name, field_name_mapping in recast_field_mapping.items():
                field_value_to_recast = attributes.get(field_name, None)
                if field_value_to_recast is not None:
                    field_value_recast = recast_field_value(
                        field_value=field_value_to_recast, **field_name_mapping
                    )
                    csv_attributes[field_name] = field_value_recast
    else:
        csv_attributes = {}

    return csv_attributes


def geolayer_to_csv(
    geolayer,
    path,
    overwrite=False,
    add_extension=False,
    delimiter=";",  # we prefer semicolon because StringList, IntegerList and FloatList
    header=True,
    null_string="",
    quote_character="",
    write_geometry=True,
    geometry_format="WKT",
    geometry_field_name="geom",
    encoding=None,
):
    """
        Save geolayer to geojson format

    :param geolayer: geolayer that we want to convert in csv,
    :param path: path to output csv,
    :param overwrite: if path exists True to overwrite it,
    :param add_extension: add .csv extension if not exists in path,
    :param delimiter: delimiter character,
    :param header: True to add header in csv
    :param null_string: format of None value in csv,
    :param quote_character: quote character in csv to describe string value,
    :param write_geometry: True to add feature geometry in csv False not,
    :param geometry_format: geometry export format (WKT or WKB or GEOJSON),
    :param geometry_field_name: name of geometry field,
    :param encoding: string encoding default utf8

    """
    # check input path and deduce output path
    output_path = path_to_file_path(
        path=path,
        geolayer_name=geolayer["metadata"]["name"],
        overwrite=overwrite,
        add_extension=add_extension,
    )

    with open(output_path, "w", encoding=encoding) as csv_file:
        string_field_name = []
        geolayer_fields_metadata = geolayer["metadata"].get("fields")
        if geolayer_fields_metadata:
            # get field_name list ordered by i_field
            field_name_list = get_field_name_list_ordered_by_i_field(
                geolayer_fields_metadata
            )
            string_field_name = [
                field_name
                for field_name in geolayer_fields_metadata
                if geolayer_fields_metadata[field_name]["type"] == "String"
            ]

        header_line = []
        if header is True:
            if geolayer_fields_metadata:
                header_line = delimiter.join(
                    [field_name for field_name in field_name_list]
                )
            if write_geometry and geolayer["metadata"].get("geometry_ref"):
                if header_line:
                    header_line = delimiter.join([header_line, geometry_field_name])
                else:
                    header_line = geometry_field_name
            header_line = [header_line]

        # scan field metadata to check if field must have to be recast
        recast_field_mapping = _get_recast_field_type_mapping(
            fields_metadata=geolayer_fields_metadata,
            geoformat_type_to_output_driver_type=geoformat_field_type_to_csv_field_type,
        )
        features_lines = [None] * len(geolayer["features"])
        for i_line, (i_feat, feature) in enumerate(geolayer["features"].items()):
            csv_feature = geoformat_feature_to_csv_feature(
                feature=feature,
                recast_field_mapping=recast_field_mapping,
                string_field_name=string_field_name,
                null_string=null_string,
                quote_character=quote_character,
                write_geometry=write_geometry,
                geometry_format=geometry_format,
            )

            # format attributes
            csv_attributes = csv_feature.get("attributes", [])
            csv_feature_line = None
            if csv_attributes:
                csv_feature_line = delimiter.join(
                    [
                        csv_attributes.get(field_name, null_string)
                        for field_name in field_name_list
                    ]
                )

            # format geometry
            if write_geometry is True:
                feature_geometry = csv_feature.get("geometry", "")
                if feature_geometry:
                    # add geometry
                    if csv_feature_line:
                        csv_feature_line = delimiter.join(
                            [csv_feature_line, feature_geometry]
                        )
                    else:
                        csv_feature_line = feature_geometry

            features_lines[i_line] = csv_feature_line

        # format and write
        csv_lines = header_line + features_lines
        csv_txt = "\n".join(csv_lines)
        csv_file.write(csv_txt)
