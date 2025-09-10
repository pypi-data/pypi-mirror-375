import copy
from geoformat.conf.error_messages import (
    field_exists
)
from geoformat.conf.format_data import value_to_iterable_value

def rename_field_in_feature(feature, old_field_name, new_field_name):
    """
    Rename field in feature

    :param feature: input feature.
    :param old_field_name: actual name of field that we want to change.
    :param new_field_name: new field's name that we want to apply.
    :return: feature with field rename
    """
    feature = copy.deepcopy(feature)
    if feature_attributes := feature.get("attributes"):
        if old_field_name in feature_attributes:
            if new_field_name not in feature_attributes:
                feature_attributes[new_field_name] = feature_attributes[old_field_name]
                del feature_attributes[old_field_name]
            else:
                raise Exception(field_exists.format(field_name=new_field_name))

    return feature

def drop_field_in_feature(feature, field_name_or_field_name_list):
    """
    Drop field (if exists) in feature

    :param feature: feature on which we want to delete field(s).
    :param field_name_or_field_name_list: name or name list of field that we want to delete.
    :return: feature without field that we want to delete.
    """
    field_name_or_field_name_list = value_to_iterable_value(field_name_or_field_name_list, output_iterable_type=list)

    feature = copy.deepcopy(feature)
    if feature_attributes := feature.get('attributes'):
        for field_name_to_drop in field_name_or_field_name_list:
            if field_name_to_drop in feature_attributes:
                del feature_attributes[field_name_to_drop]

        # delete attributes key if there is no attributes data in feature
        if not feature_attributes:
            del feature['attributes']

    return feature


def drop_field_that_not_exists_in_feature(feature, not_deleting_field_name_or_field_name_list):
    """
    Drop field in feature that are not specified in not_deleting_field_name_or_field_name_list variable.

    :param feature:  feature on which we want to delete field(s).
    :param not_deleting_field_name_or_field_name_list: name or name list of field that we want to keep.
    :return: feature with field that we want to keep.
    """
    not_deleting_field_name_or_field_name_list  = value_to_iterable_value(
        value=not_deleting_field_name_or_field_name_list,
        output_iterable_type=set
    )
    if feature_attributes := feature.get('attributes'):
        feature_field_name_set = set(list(feature_attributes.keys()))
        field_name_to_drop_set = feature_field_name_set - not_deleting_field_name_or_field_name_list
        for field_name_to_drop in field_name_to_drop_set:
            feature = drop_field_in_feature(feature=feature, field_name_or_field_name_list=field_name_to_drop)

    return feature