import copy

from geoformat.conf.format_data import value_to_iterable_value
from geoformat.conversion.feature_conversion import (
    feature_filter
)
from geoformat.conversion.geometry_conversion import (
    multi_geometry_to_single_geometry,
    geometry_type_to_2d_geometry_type,
    geometry_to_2d_geometry,
    reproject_geometry
)

from geoformat.conversion.feature_conversion import feature_serialize, feature_deserialize

from geoformat.manipulation.metadata_manipulation import drop_field_that_not_exists_in_metadata


def multi_geometry_to_single_geometry_geolayer(geolayer):
    """
    Transform multi geometry geolayer (MultiPolygon, MultiLineString, MultiPoint) to single geometry geolayer (
    """
    # creation de l'output en copiant les metadata de l'input
    geolayer_out = copy.deepcopy(geolayer)
    bbox_extent = False
    del geolayer_out['features']
    if 'geometry_ref' in geolayer_out['metadata']:
        geolayer_out['metadata']['geometry_ref']['type'] = set()
        if 'extent' in geolayer_out['metadata']['geometry_ref']:
            bbox_extent = True

    # boucle et transformation des géométries multi part en single part
    new_i_feat = 0
    geolayer_out['features'] = {}
    for i_feat, feature in geolayer['features'].items():

        # if feature is serialized
        if 'feature_serialize' in geolayer['metadata']:
            if geolayer['metadata']['feature_serialize']:
                feature = feature_deserialize(serialized_feature=feature, bbox=False)

        geometry = feature['geometry']
        if geometry:
            for new_geometry in multi_geometry_to_single_geometry(geometry, bbox=bbox_extent):
                new_feature = {}
                if "attributes" in feature:
                    new_feature["attributes"] = feature['attributes']  # we add attributes first for better read

                new_feature["geometry"] = new_geometry


                # update geolayer metadata geometry type
                geolayer_out['metadata']['geometry_ref']['type'].update(set([new_geometry['type']]))

                # if feature is serialized
                if 'feature_serialize' in geolayer['metadata']:
                    if geolayer['metadata']['feature_serialize']:
                        new_feature = feature_serialize(feature=new_feature)

                geolayer_out['features'][new_i_feat] = new_feature
                new_i_feat += 1

    return geolayer_out


def geolayer_to_2d_geolayer(input_geolayer):
    """
    Transform geolayer with x dimension to geolayer who contain geometries with 2d dimension only.

    :param input_geolayer: geolayer to transform
    :return: 2d geometry geolayer
    """
    new_geolayer = {'metadata': copy.deepcopy(input_geolayer['metadata']), 'features': {}}

    # if geometry in geolayer
    if input_geolayer['metadata'].get('geometry_ref'):
        input_geometry_type = input_geolayer['metadata']['geometry_ref']['type']
        if isinstance(input_geometry_type, (list, tuple, set)):
            new_geometry_type = set()
            for geom_type in input_geometry_type:
                new_geometry_type.update([geometry_type_to_2d_geometry_type(geom_type)])
        else:
            new_geometry_type = geometry_type_to_2d_geometry_type(input_geometry_type)
        new_geolayer['metadata']['geometry_ref']['type'] = new_geometry_type

        if 'extent' in new_geolayer['metadata']['geometry_ref']:
            bbox_extent = True
        else:
            bbox_extent = False

    for i_feat, input_feature in input_geolayer['features'].items():
        if 'feature_serialize' in input_geolayer['metadata']:
            if input_geolayer['metadata']['feature_serialize'] == True:
                input_feature = eval(input_feature)

        output_feature = copy.deepcopy(input_feature)

        if 'geometry' in input_feature:
            input_geometry = input_feature['geometry']
            new_geometry = geometry_to_2d_geometry(input_geometry, bbox=bbox_extent)
            output_feature['geometry'] = new_geometry

        if 'feature_serialize' in input_geolayer['metadata']:
            if input_geolayer['metadata']['feature_serialize'] == True:
                output_feature = str(output_feature)

        new_geolayer['features'][i_feat] = output_feature

    return new_geolayer


def create_geolayer_from_i_feat_list(
        geolayer,
        i_feat_list,
        output_geolayer_name=None,
        field_name_filter=None,
        geometry_type_filter=None,
        bbox_filter=None,
        serialize=False,
        reset_i_feat=True
):
    """
    Create a new layer with i_feat_list from an input layer
    """
    i_feat_list = value_to_iterable_value(value=i_feat_list, output_iterable_type=list)

    new_geolayer_metadata = dict(geolayer['metadata'])
    if 'index' in new_geolayer_metadata:
        del new_geolayer_metadata['index']

     # rename geolayer
    if output_geolayer_name:
        new_geolayer_metadata['name'] = output_geolayer_name

    if field_name_filter:
        new_geolayer_metadata = drop_field_that_not_exists_in_metadata(
            metadata=new_geolayer_metadata,
            not_deleting_field_name_or_field_name_list=field_name_filter)

    if 'index' in new_geolayer_metadata:
        del new_geolayer_metadata['index']


    if geometry_type_filter:
        # erase geometry type in geometry ref
        if 'geometry_ref' in new_geolayer_metadata:
            new_geolayer_metadata['geometry_ref']['type'] = set()

    new_geolayer = {
        'metadata': new_geolayer_metadata
    }

    if serialize is True:
        new_geolayer['metadata']['feature_serialize'] = True

    new_geolayer['features'] = {}
    for i, i_feat in enumerate(i_feat_list):

        # if we have to reset i_feat
        if reset_i_feat:
            new_i_feat = i
        else:
            new_i_feat = i_feat

        # add feature to geolayer
        feature = geolayer['features'][i_feat]
        new_feature = feature_filter(
            feature=feature,
            serialize=serialize,
            field_name_filter=field_name_filter,
            geometry_type_filter=geometry_type_filter,
            bbox_filter=bbox_filter,
            bbox=False
        )
        if geometry_type_filter:
            # update geolayer geometry metadata
            if 'geometry' in new_feature:
                new_geolayer['metadata']['geometry_ref']['type'].update([new_feature['geometry']['type']])

        new_geolayer['features'][new_i_feat] = new_feature

    return new_geolayer


def reproject_geolayer(geolayer, out_crs, in_crs=None, precision=None):
    """
    Reproject geolayer from crs to an other

    :param geolayer: input geolayer.
    :param out_crs: new crs.
    :param in_crs:  input geolayer crs (if not present in geolayer metadata).
    :return:
    """

    geolayer = copy.deepcopy(geolayer)
    if not in_crs:
        in_crs = geolayer['metadata']['geometry_ref']['crs']

    # change metadata
    geolayer['metadata']['geometry_ref']['crs'] = out_crs


    # reproject geometry
    for i_feat in geolayer['features']:
        feature = geolayer['features'][i_feat]

        # if geometry in feature
        if 'geometry' in feature.keys():
            feature_geometry = feature['geometry']
            new_geometry = reproject_geometry(
                geometry=feature_geometry,
                in_crs=in_crs,
                out_crs=out_crs,
                precision=precision
            )

            # assign new geometry
            feature['geometry'] = new_geometry


    return geolayer
