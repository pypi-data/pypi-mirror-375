import copy

from geoformat.conf.error_messages import metadata_fields_not_same, metadata_geometry_crs
from geoformat.conversion.feature_conversion import feature_serialize, feature_deserialize
from geoformat.conversion.metadata_conversion import get_field_name_list_ordered_by_i_field


def union_metadata(metadata_a, metadata_b, metadata_name, field_name_filter=None, feature_serialize=False):
    """

    """
    new_metadata = {"name": metadata_name}
    # check if field metadata are equal
    if 'fields' in metadata_a and 'fields' in metadata_b:

        if metadata_a['fields'].keys() != metadata_b['fields'].keys():
            raise Exception(metadata_fields_not_same)
        else:
            field_metadata_a = metadata_a['fields']
            field_metadata_b = metadata_b['fields']
            # get order field
            if field_name_filter:
                field_name_list = field_name_filter
            else:
                field_name_list = get_field_name_list_ordered_by_i_field(fields_metadata=field_metadata_a)
            for i_field, field_name in enumerate(field_name_list):
                new_metadata['fields'] = {}
                field_name_metadata_a = field_metadata_a[field_name]
                field_name_metadata_b = field_metadata_b[field_name]
                # type
                if field_type := field_name_metadata_a['type'] != field_name_metadata_b['type']:
                    raise Exception()
                else:
                    new_metadata['fields'][field_name] = {'type': field_type}
                # width
                if field_width_a := field_name_metadata_a.get('width'):
                    field_width_b = field_name_metadata_b['width']
                    field_width = max((field_width_a, field_width_b))
                    new_metadata['fields'][field_name]['width'] = field_width
                # precision
                if field_precision_a := field_name_metadata_a.get('precision'):
                    field_precision_b = field_name_metadata_b['precision']
                    field_precision = max((field_precision_a, field_precision_b))
                    new_metadata['fields'][field_name]['precision'] = field_precision
                # index
                new_metadata['fields'][field_name]['index'] = i_field
            new_metadata['fields'] = copy.deepcopy(metadata_a['fields'])

    # if geometry
    metadata_a_geometry_ref = metadata_a.get('geometry_ref')
    metadata_b_geometry_ref = metadata_b.get('geometry_ref')
    if metadata_a_geometry_ref is not None or metadata_b_geometry_ref is not None:
        metadata_a_geometry_ref_type = copy.deepcopy(metadata_a_geometry_ref.get('type', set()))
        metadata_b_geometry_ref_type = copy.deepcopy(metadata_b_geometry_ref.get('type', set()))
        new_metadata_geometry_type = metadata_a_geometry_ref_type.union(metadata_b_geometry_ref_type)

        new_metadata['geometry_ref'] = {"type": new_metadata_geometry_type}
        metadata_a_geometry_ref_crs = metadata_a_geometry_ref.get('crs')
        metadata_b_geometry_ref_crs = metadata_b_geometry_ref.get('crs')
        if metadata_a_geometry_ref_crs or metadata_b_geometry_ref_crs:
            if metadata_a_geometry_ref_crs and metadata_b_geometry_ref_crs is None:
                crs = metadata_a_geometry_ref_crs
            elif metadata_b_geometry_ref_crs is None and metadata_b_geometry_ref_crs:
                crs = metadata_b_geometry_ref_crs
            else:
                if metadata_a_geometry_ref_crs != metadata_b_geometry_ref_crs:
                    raise Exception(metadata_geometry_crs)
                else:
                    crs = metadata_b_geometry_ref_crs
            new_metadata['geometry_ref']['crs'] = crs

    # if feature serialize
    if feature_serialize is True:
        new_metadata['feature_serialize'] = feature_serialize

    return new_metadata


def union_geolayer(geolayer_list, geolayer_name, serialize=False):
    """
    Union geolayers with compatible fields structure and non mixed coordinates reference system
    """
    for i_geolayer, geolayer in enumerate(geolayer_list):
        geolayer_metadata = geolayer['metadata']
        if i_geolayer == 0:
            previ_metadata = geolayer_metadata
        else:
            merge_metadata = union_metadata(metadata_a=previ_metadata, metadata_b=geolayer_metadata,
                                            metadata_name=geolayer_name, feature_serialize=serialize)
            previ_metadata = geolayer_metadata

    output_geolayer = {"metadata": merge_metadata, "features": {}}

    output_i_feat = 0
    for geolayer in geolayer_list:
        for i_feat, feature in geolayer['features'].items():
            # serialize data
            if serialize is True and geolayer['metadata'].get('feature_serialize', False) is False:
                feature = feature_serialize(feature=feature)
            elif serialize is False and geolayer['metadata'].get('feature_serialize', False) is True:
                feature = feature_deserialize(serialized_feature=feature)

            output_geolayer["features"][output_i_feat] = feature
            output_i_feat += 1

    return output_geolayer
