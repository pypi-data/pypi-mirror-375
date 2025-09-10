import hashlib

from geoformat.conf.error_messages import (
    variables_must_be_true,
    variable_must_be_fill,
)
from geoformat.conversion.geometry_conversion import  geometry_to_wkb
from geoformat.conversion.metadata_conversion import  get_field_name_list_ordered_by_i_field


def get_feature_attributes_hash(feature_attributes, field_attributes_field_name_order):
    """
    return sha256 of feature attributes.
    We order field in attributes with field_attributes_field_name_order as specified in geolayer
    field order metadata. -> We do that to compare feature attributes with None value (because when a value is None in
    a feature we are not obliged to add field with None value in it).

    :param feature_attributes: feature attributes to hash
    :param field_attributes_field_name_order: list/tuple of field name order
    :return: sha256 or feature attributes
    """
    # if feature_attributes and field_attributes_field_name_order:
    if field_attributes_field_name_order:
        if feature_attributes is None:
            feature_attributes = {}
        ordered_value_list = [None] * len(field_attributes_field_name_order)
        for i_field, field_name in enumerate(field_attributes_field_name_order):
            ordered_value_list[i_field] = (field_name, feature_attributes.get(field_name))
    else:
        ordered_value_list = []

    return hashlib.sha256(str(ordered_value_list).encode('utf8')).hexdigest()


def get_feature_geometry_hash(feature_geometry):
    """
    return sha256 of feature geometry.
    feature geometry is convert in wkb, and we make a hash of this.

    :param feature_geometry: feature geometry
    :return: sha256 or feature geometry
    """
    if feature_geometry:
        geometry_to_hash = geometry_to_wkb(feature_geometry)
    else:
        geometry_to_hash = ''.encode('utf8')

    return hashlib.sha256(geometry_to_hash).hexdigest()


def get_feature_hash(feature, field_attributes_field_name_order=None, attribute_hash=True, geometry_hash=True):
    """
    return sha 256 of feature.

    :param feature: feature to hash
    :param field_attributes_field_name_order: list/tuple of field name order
    :param attribute_hash: True if you want attribute hash
    :param geometry_hash: True if you want geometry hash
    :return: sha256 of feature
    """
    if attribute_hash is False and geometry_hash is False:
        raise Exception(variables_must_be_true.format(variables=' or '.join(['attribute_hash', 'geometry_hash'])))
    if attribute_hash is True and feature.get('attributes') and not field_attributes_field_name_order:
        raise Exception(variable_must_be_fill.format(variable_name="field_attributes_field_name_order"))

    feature_attributes_hash = ''
    feature_geometry_hash = ''
    feature_attributes = feature.get("attributes")
    if attribute_hash is True and feature_attributes and field_attributes_field_name_order:
        feature_attributes_hash = get_feature_attributes_hash(feature_attributes=feature_attributes,
                                                              field_attributes_field_name_order=field_attributes_field_name_order)
    feature_geometry = feature.get("geometry")
    if geometry_hash is True and feature_geometry:
        feature_geometry_hash = get_feature_geometry_hash(feature_geometry=feature_geometry)

    feature_hash = hashlib.sha256((feature_attributes_hash + feature_geometry_hash).encode('utf8')).hexdigest()

    return feature_hash


def get_duplicate_features(geolayer,  check_attribute_duplicate=True, check_geometry_duplicate=True):
    """
    Scan geolayer and return duplicate feature.
    You can optionally choose if you want to determine duplication, resume by this table
        | geometry_duplicate |attribute_duplicate | meaning                  |
        |--------------------|--------------------|--------------------------|
        | True               | True               | geometry and attributes  |
        | True               | False              | geometry only            |
        | False              | True               | attributes only          |
        | False              | False              | Error                    |

    :param geolayer: input geolayer for which we want to know the duplicated entities
    :param check_attribute_duplicate: True if you want to check attributes
    :param check_geometry_duplicate: True if you want check geometry
    :yield: duplicate feature i_feat
    """

    if check_geometry_duplicate is False and check_attribute_duplicate is False:
        raise Exception(variables_must_be_true.format(variables=' or '.join(['geometry_duplicate', 'attribute_duplicate'])))

    # initialize checking variable
    field_attributes_field_name_order = {}
    if geolayer['metadata'].get('fields'):
        field_attributes_field_name_order = get_field_name_list_ordered_by_i_field(fields_metadata=geolayer['metadata']['fields'])

    duplicate_hash = set()
    for i_feat, feature in geolayer['features'].items():
        feature_hash = get_feature_hash(feature=feature, field_attributes_field_name_order=field_attributes_field_name_order, attribute_hash=check_attribute_duplicate, geometry_hash=check_geometry_duplicate)

        if feature_hash in duplicate_hash:
            yield i_feat

        duplicate_hash.update([feature_hash])
