import copy

from geoformat.conf.error_messages import (
    field_exists,
    metadata_geometry_ref_not_found,
    metadata_geometry_ref_type_not_match,
    geometry_ref_metadata,
    geometry_ref_feature
)
from geoformat.conf.format_data import (
    value_to_iterable_value
)
from geoformat.manipulation.feature_manipulation import (
    rename_field_in_feature,
    drop_field_that_not_exists_in_feature
)
from geoformat.manipulation.metadata_manipulation import (
    drop_field_that_not_exists_in_metadata,
    rename_field_in_metadata
)


def _merge_metadata_rename_field(metadata, field_to_rename_dict, rename_field_correspondance):
    """
    function build for merge_metadata
    """
    for i_field, (old_field_name, new_field_name) in enumerate(field_to_rename_dict.items()):
        metadata = rename_field_in_metadata(
            metadata=metadata,
            old_field_name=old_field_name,
            new_field_name=new_field_name
        )
        if i_field == 0:
            rename_field_correspondance = {}
        rename_field_correspondance[old_field_name] = new_field_name

    return metadata, rename_field_correspondance


def merge_metadata(
        metadata_a,
        metadata_b,
        geolayer_name,
        field_name_filter_a=None,
        field_name_filter_b=None,
        geometry_ref="metadata_a",
        rename_output_field_from_geolayer_a="auto",
        rename_output_field_from_geolayer_b="auto",
):
    """
    When a join is performed between two geolayers : it results a new geolayer whose attribute component is the result
    of the merging of fields metadata.
    You can optionally choose here to keep the geometry metadata of this or that geolayer.

    In output we receive not only a new metadata but also a fields correspondance table : in case fields with the same
    name exist between the two geolayers a mapping table is provided as output.

    :param metadata_a: first metadata to merge
    :param metadata_b: second metadata to merge
    :param geolayer_name: new name of geolayer
    :param field_name_filter_a: field name filter for metadata_a
    :param field_name_filter_b: field name filter for metadata_b
    :param geometry_ref: name the metadata that keep the geometry_ref metadata (default : metadata_a)
    :param rename_geolayer_field: indicate when there is name field collision what we do. Two option :
                                - "auto" : rename automatiquely the field
                                - a dict with this format : {
                                "metadata_a":
                                    {old_field_name_a: new_field_name_a,
                                     old_filed_name_b: new_field_name_b ...},
                                "metadata_b:
                                    {old_field_name_c: new_field_name_c,
                                     old_filed_name_d: new_field_name_d ...},
                                }
    :return: the merged metadata
    """
    metadata_merged = copy.deepcopy(metadata_a)
    metadata_b = copy.deepcopy(metadata_b)
    field_name_filter_a = value_to_iterable_value(value=field_name_filter_a, output_iterable_type=list)
    field_name_filter_b = value_to_iterable_value(value=field_name_filter_b, output_iterable_type=list)

    # delete geometry ref
    if 'geometry_ref' in metadata_merged and geometry_ref == 'metadata_b':
        del metadata_merged['geometry_ref']

    # add new name to merge metadata
    metadata_merged["name"] = geolayer_name

    # clean index and matrix
    if 'index' in metadata_merged:
        del metadata_merged['index']
    if 'matrix' in metadata_merged:
        del metadata_merged['matrix']

    # drop useless field
    if field_name_filter_a is not None and metadata_merged.get('fields'):
        metadata_merged = drop_field_that_not_exists_in_metadata(
            metadata=metadata_merged,
            not_deleting_field_name_or_field_name_list=field_name_filter_a
        )
    if field_name_filter_b is not None and metadata_b.get('fields'):
        metadata_b = drop_field_that_not_exists_in_metadata(
            metadata=metadata_b,
            not_deleting_field_name_or_field_name_list=field_name_filter_b
        )

    # rename field if necessary
    rename_field_correspondance_a = {}
    if rename_output_field_from_geolayer_a != 'auto':
        metadata_merged, rename_field_correspondance_a = _merge_metadata_rename_field(
            metadata=metadata_merged,
            field_to_rename_dict=rename_output_field_from_geolayer_a,
            rename_field_correspondance=rename_field_correspondance_a)
    rename_field_correspondance_b = {}
    if rename_output_field_from_geolayer_b != 'auto':
        metadata_b, rename_field_correspondance_b = _merge_metadata_rename_field(
            metadata=metadata_b,
            field_to_rename_dict=rename_output_field_from_geolayer_b,
            rename_field_correspondance=rename_field_correspondance_b)

    # add fields in metadata
    for key, value in metadata_b.items():
        if key == 'fields':
            for geolayer_b_field_name, geolayer_b_field_metadata in metadata_b[key].items():
                if 'fields' in metadata_merged:
                    # if geolayer_b_field_name exists in geolayer_a
                    if metadata_merged['fields'].get(geolayer_b_field_name):
                        if rename_output_field_from_geolayer_b == 'auto':
                            exists = True
                            it = 1
                            new_field_name = geolayer_b_field_name
                            while exists is True:
                                new_field_name = f'{new_field_name}{it}'
                                if new_field_name in metadata_merged['fields']:
                                    it += 1
                                else:
                                    exists = False
                            # add new_field_name to rename_field_correspondance_b
                            rename_field_correspondance_b[geolayer_b_field_name] = new_field_name
                        else:
                            if geolayer_b_field_name in metadata_merged['fields']:
                                raise Exception(field_exists.format(field_name=geolayer_b_field_name))
                    else:
                        new_field_name = geolayer_b_field_name
                else:
                    # add fields key in metadata
                    metadata_merged['fields'] = {}
                    new_field_name = geolayer_b_field_name

                # create new field in metadata
                metadata_merged['fields'][new_field_name] = dict(geolayer_b_field_metadata)
                # reorder index
                metadata_merged['fields'][new_field_name]['index'] = len(metadata_merged['fields']) - 1

        # update geometry ref if necessary
        if key == 'geometry_ref':
            if geometry_ref == 'metadata_a':
                pass
            elif geometry_ref == 'metadata_b':
                metadata_merged['geometry_ref'] = copy.deepcopy(metadata_b['geometry_ref'])
            else:
                raise Exception(geometry_ref_metadata)

    return {
        'metadata': metadata_merged,
        'fields_correspondance_a': rename_field_correspondance_a,
        'fields_correspondance_b': rename_field_correspondance_b
    }


def merge_feature(
    feature_a,
    feature_b,
    merge_metadata=None,
    field_name_filter_a=None,
    field_name_filter_b=None,
    rename_fields_a=None,
    rename_fields_b=None,
    geometry_ref='feature_a'
):
    """
    Merge two features in one new feature.

    :param feature_a: first feature to merge
    :param feature_b: second feature to merge
    :param merge_metadata: if we want add a constraint metadata to merge. Warning : here metadata are not updated by
    feature that we want to merge. It is a constraint to check if the new feature will be compatible with given metadata
    :param field_name_filter_a:  field name filter for feature_a
    :param field_name_filter_b:  field name filter for feature_b
    :param rename_fields_a: rename field mapping for feature_a
    :param rename_fields_b: rename field mapping for feature_b
    :param geometry_ref: feature that keep geometry references (default value : feature_a)
    :return: merged result of feature_a and feature_bgeo
    """
    feature_a = copy.deepcopy(feature_a)
    feature_b = copy.deepcopy(feature_b)

    # delete useless field
    if field_name_filter_a:
        feature_a = drop_field_that_not_exists_in_feature(
            feature=feature_a,
            not_deleting_field_name_or_field_name_list=field_name_filter_a
        )
    if field_name_filter_b:
        feature_b = drop_field_that_not_exists_in_feature(
            feature=feature_b,
            not_deleting_field_name_or_field_name_list=field_name_filter_b
        )

    # rename fields
    if rename_fields_a:
        for old_field_name, new_field_name in rename_fields_a.items():
            feature_a = rename_field_in_feature(
                feature=feature_a,
                old_field_name=old_field_name,
                new_field_name=new_field_name
            )

    if rename_fields_b:
        for old_field_name, new_field_name in rename_fields_b.items():
            feature_b = rename_field_in_feature(
                feature=feature_b,
                old_field_name=old_field_name,
                new_field_name=new_field_name
            )

    # check there is no field_name collision between feature
    feature_field_name_collision = set(feature_a.get('attributes', {}).keys()).intersection(set(feature_b.get('attributes', {}).keys()))
    if len(feature_field_name_collision) > 0:
        error_message_list = []
        for field_name in feature_field_name_collision:
            error_message_list.append(field_exists.format(field_name=field_name))
        raise Exception('/n'.join(error_message_list))

    # write attributes
    output_feature = {}
    feature_attributes_list = []
    if feature_a_attributes := feature_a.get('attributes'):
        feature_attributes_list.append(feature_a_attributes)
    if feature_b_attributes := feature_b.get('attributes'):
        feature_attributes_list.append(feature_b_attributes)

    # if merge metadata we check fields and keep only matching fields
    if merge_metadata:
        if fields_metadata := merge_metadata.get('fields'):
            for field_name, field_metadata in fields_metadata.items():
                for feature_attributes in feature_attributes_list:
                    if field_name in feature_attributes:
                        if 'attributes' not in output_feature:
                            output_feature['attributes'] = {}
                        output_feature['attributes'][field_name] = feature_attributes[field_name]

    else:
        for feature_attributes in feature_attributes_list:
            for field_name, field_value in feature_attributes.items():
                if 'attributes' not in output_feature:
                    output_feature['attributes'] = {}
                output_feature['attributes'][field_name] = field_value

    # write geometry
    if geometry_ref == 'feature_a':
        output_feature_geometry = feature_a.get('geometry')
    elif geometry_ref == 'feature_b':
        output_feature_geometry = feature_b.get('geometry')
    else:
        raise Exception(geometry_ref_feature)

    # add geometry to feature
    if output_feature_geometry is not None:
        if merge_metadata:
            if metadata_geometry :=merge_metadata.get('geometry_ref'):
                if output_feature_geometry['type'] not in metadata_geometry['type']:
                    raise Exception(metadata_geometry_ref_type_not_match)
            else:
                raise Exception(metadata_geometry_ref_not_found)

        output_feature['geometry'] = output_feature_geometry

    return output_feature
